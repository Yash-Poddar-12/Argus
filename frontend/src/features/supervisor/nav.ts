import type { NavItem } from "@/components/layout/AppShell";

// supervisor navigation. Adding a page = one line here + a route folder in src/app/supervisor/.
export const SUPERVISOR_NAV: NavItem[] = [
  { href: "/supervisor/overview", label: { en: { label: "Overview" }, hi: { label: "अवलोकन" }, ta: { label: "மேலோட்டம்" } } },
  { href: "/supervisor/operators", label: { en: { label: "Operators" }, hi: { label: "ऑपरेटर" }, ta: { label: "இயக்குநர்கள்" } } },
  { href: "/supervisor/machines", label: { en: { label: "Machines" }, hi: { label: "मशीनें" }, ta: { label: "இயந்திரங்கள்" } } },
  { href: "/supervisor/sites", label: { en: { label: "Sites & Zones" }, hi: { label: "साइट और ज़ोन" }, ta: { label: "தளங்கள் & மண்டலங்கள்" } } },
  { href: "/supervisor/tasks", label: { en: { label: "Tasks" }, hi: { label: "कार्य" }, ta: { label: "பணிகள்" } } },
  { href: "/supervisor/assignments", label: { en: { label: "Assignments" }, hi: { label: "असाइनमेंट" }, ta: { label: "ஒதுக்கீடுகள்" } } },
  { href: "/supervisor/site-map", label: { en: { label: "Site Map" }, hi: { label: "साइट मानचित्र" }, ta: { label: "தள வரைபடம்" } } },
  { href: "/supervisor/safety", label: { en: { label: "Safety & Hazards" }, hi: { label: "सुरक्षा" }, ta: { label: "பாதுகாப்பு" } } },
  { href: "/supervisor/site-intel", label: { en: { label: "Site Intelligence" }, hi: { label: "साइट इंटेलिजेंस" }, ta: { label: "தள நுண்ணறிவு" } } },
  { href: "/supervisor/scenarios", label: { en: { label: "What-if Scenarios" }, hi: { label: "क्या-होगा परिदृश्य" }, ta: { label: "என்ன-என்றால்" } } },
  { href: "/supervisor/training-admin", label: { en: { label: "Training Admin" }, hi: { label: "प्रशिक्षण प्रबंधन" }, ta: { label: "பயிற்சி நிர்வாகம்" } } },
  { href: "/supervisor/analytics", label: { en: { label: "Analytics" }, hi: { label: "विश्लेषण" }, ta: { label: "பகுப்பாய்வு" } } },
];
