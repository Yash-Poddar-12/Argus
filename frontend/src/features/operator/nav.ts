import type { NavItem } from "@/components/layout/AppShell";

// operator navigation. Adding a page = one line here + a route folder in src/app/operator/.
export const OPERATOR_NAV: NavItem[] = [
  { href: "/operator/my-day", label: { en: { label: "My Day" }, hi: { label: "मेरा दिन" }, ta: { label: "என் நாள்" } } },
  { href: "/operator/my-machine", label: { en: { label: "My Machine" }, hi: { label: "मेरी मशीन" }, ta: { label: "என் இயந்திரம்" } } },
  { href: "/operator/my-tasks", label: { en: { label: "My Tasks" }, hi: { label: "मेरे कार्य" }, ta: { label: "என் பணிகள்" } } },
  { href: "/operator/my-safety", label: { en: { label: "My Safety" }, hi: { label: "मेरी सुरक्षा" }, ta: { label: "என் பாதுகாப்பு" } } },
  { href: "/operator/my-performance", label: { en: { label: "My Performance" }, hi: { label: "मेरा प्रदर्शन" }, ta: { label: "என் செயல்திறன்" } } },
  { href: "/operator/training", label: { en: { label: "My Training" }, hi: { label: "मेरा प्रशिक्षण" }, ta: { label: "என் பயிற்சி" } } },
  { href: "/operator/copilot", label: { en: { label: "AI Copilot" }, hi: { label: "एआई सहायक" }, ta: { label: "AI உதவியாளர்" } } },
];
