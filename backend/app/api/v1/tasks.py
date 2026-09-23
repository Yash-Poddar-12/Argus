"""Tasks, assignments, operator day, machine confirmation, pre-checks and lifecycle (thin routes)."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.dependencies import Principal, current_principal, require_permission
from app.domain.platform import service as platform
from app.domain.tasks import assignments, lifecycle, reporting, service
from app.domain.tasks.schemas import (
    AssignmentCreate,
    AssignmentDTO,
    AssignmentUpdate,
    AssignRequest,
    ConfirmMachineRequest,
    ConfirmMachineResponse,
    PrecheckResultDTO,
    PrecheckSubmit,
    PrecheckTemplateDTO,
    SessionDTO,
    TaskActionResponse,
    TaskCreate,
    TaskDTO,
    TaskStatus,
    TaskSummary,
    TaskUpdate,
    TodayTask,
)

router = APIRouter()


@router.post("/tasks", response_model=TaskDTO, status_code=201, tags=["tasks"])
async def create_task(body: TaskCreate, p: Principal = Depends(require_permission("tasks:write"))):
    return TaskDTO.model_validate(await service.create_task(p, body))


@router.get("/tasks/{task_id}", response_model=TaskDTO, tags=["tasks"])
async def get_task(task_id: str, p: Principal = Depends(current_principal)):
    return TaskDTO.model_validate(await service.read_task(p, task_id))


@router.patch("/tasks/{task_id}", response_model=TaskDTO, tags=["tasks"])
async def update_task(task_id: str, body: TaskUpdate, p: Principal = Depends(require_permission("tasks:write"))):
    return TaskDTO.model_validate(await service.update_task(p, task_id, body))


@router.get("/sites/{site_id}/tasks", response_model=list[TaskDTO], tags=["tasks"])
async def list_site_tasks(site_id: str, status: TaskStatus | None = None, day: date | None = Query(None, alias="date"),
                          p: Principal = Depends(require_permission("tasks:read"))):
    return [TaskDTO.model_validate(t) for t in await service.list_site_tasks(p, site_id, status, day)]


@router.post("/tasks/{task_id}/assign", response_model=AssignmentDTO, status_code=201, tags=["assignments"])
async def assign_task(task_id: str, body: AssignRequest, p: Principal = Depends(require_permission("tasks:assign"))):
    return AssignmentDTO.model_validate(await assignments.assign(p, task_id, body.operator_id, body.machine_id, body.replace))


@router.post("/assignments", response_model=AssignmentDTO, status_code=201, tags=["assignments"])
async def create_assignment(body: AssignmentCreate, p: Principal = Depends(require_permission("tasks:assign"))):
    return AssignmentDTO.model_validate(
        await assignments.assign(p, body.task_id, body.operator_id, body.machine_id, body.replace))


@router.patch("/assignments/{assignment_id}", response_model=AssignmentDTO, tags=["assignments"])
async def patch_assignment(assignment_id: str, body: AssignmentUpdate,
                           p: Principal = Depends(require_permission("tasks:assign"))):
    return AssignmentDTO.model_validate(
        await assignments.update_assignment(p, assignment_id, status=body.status, machine_id=body.machine_id))


@router.get("/operators/{operator_id}/tasks/today", response_model=list[TodayTask], tags=["operator-day"])
async def operator_tasks_today(operator_id: str, day: date | None = Query(None, alias="date"),
                               p: Principal = Depends(current_principal)):
    operator = await platform.get_operator(operator_id)
    p.ensure_operator(operator_id, operator.site_id if operator else None)
    return await reporting.tasks_today(operator_id, day)


@router.post("/operators/{operator_id}/machine/confirm", response_model=ConfirmMachineResponse, tags=["operator-day"])
async def confirm_machine(operator_id: str, body: ConfirmMachineRequest,
                          p: Principal = Depends(require_permission("tasks:execute"))):
    c = await lifecycle.confirm_machine(p, operator_id, body.machine_id)
    return ConfirmMachineResponse(operator_id=c.operator_id, machine_id=c.machine_id, confirmed_at=c.confirmed_at)


@router.get("/machines/{machine_id}/precheck", response_model=PrecheckTemplateDTO, tags=["precheck"])
async def get_precheck(machine_id: str, p: Principal = Depends(current_principal)):
    machine = await platform.get_machine(machine_id)
    p.ensure_site(machine.site_id if machine else None)
    return PrecheckTemplateDTO.model_validate(await lifecycle.precheck_template(machine_id))


@router.post("/machines/{machine_id}/precheck", response_model=PrecheckResultDTO, status_code=201, tags=["precheck"])
async def post_precheck(machine_id: str, body: PrecheckSubmit, p: Principal = Depends(require_permission("tasks:execute"))):
    return PrecheckResultDTO.model_validate(
        await lifecycle.submit_precheck(p, machine_id, [a.model_dump() for a in body.results]))


def _action(fn):
    async def endpoint(task_id: str, p: Principal = Depends(require_permission("tasks:execute"))):
        task, sess = await fn(p, task_id)
        return TaskActionResponse(task=TaskDTO.model_validate(task), session=SessionDTO.model_validate(sess))
    return endpoint


for _name, _fn in (("start", lifecycle.start), ("pause", lifecycle.pause), ("resume", lifecycle.resume),
                   ("complete", lifecycle.complete)):
    router.add_api_route(f"/tasks/{{task_id}}/{_name}", _action(_fn), methods=["POST"], response_model=TaskActionResponse,
                         tags=["task-lifecycle"], name=f"{_name}_task", summary=f"{_name.title()} task")


@router.get("/tasks/{task_id}/summary", response_model=TaskSummary, tags=["task-lifecycle"])
async def task_summary(task_id: str, p: Principal = Depends(current_principal)):
    await service.read_task(p, task_id)  # permission/scope check
    return await reporting.summary(task_id)
