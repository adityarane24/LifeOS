import { useEffect,useState } from "react";
import Dashboard from "../pages/Dashboard";
import Tasks from "../pages/Tasks";
import Goals from "../pages/Goals";
import Habits from "../pages/Habits";
import Projects from "../pages/Projects";
import Activity from "../pages/Activity";
import Analytics from "../pages/Analytics";
import Settings from "../pages/Settings";

type Page =
  | "dashboard"
  | "tasks"
  | "goals"
  | "habits"
  | "projects"
  | "activity"
  | "analytics"
  | "settings";

const navigation: { id: Page; label: string }[] = [
  { id: "dashboard", label: "Dashboard" },
  { id: "tasks", label: "Tasks" },
  { id: "goals", label: "Goals" },
  { id: "habits", label: "Habits" },
  { id: "projects", label: "Projects" },
  { id: "activity", label: "Activity" },
  { id: "analytics", label: "Analytics" },
];

function PageContent({ page }: { page: Page }) {
  switch (page) {
    case "tasks":
      return <Tasks />;
    case "goals":
      return <Goals />;
    case "habits":
      return <Habits />;
    case "projects":
      return <Projects />;
    case "activity":
      return <Activity />;
    case "analytics":
      return <Analytics />;
    case "settings":
      return <Settings />;
    default:
      return <Dashboard />;
  }
}

export default function AppLayout() {
  const [activePage, setActivePage] = useState<Page>("dashboard");

  useEffect(() => {
    function handleLifeOSNavigation(event: Event) {
      const customEvent = event as CustomEvent<string>;
      const page = customEvent.detail as Page;

      setActivePage(page);
    }

    window.addEventListener(
      "lifeos:navigate",
      handleLifeOSNavigation,
    );

    return () => {
      window.removeEventListener(
        "lifeos:navigate",
        handleLifeOSNavigation,
      );
    };
  }, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <strong>LifeOS</strong>
          <span>Personal Operating System</span>
        </div>

        <nav className="navigation">
          {navigation.map((item) => (
            <button
              key={item.id}
              type="button"
              className={activePage === item.id ? "nav-item active" : "nav-item"}
              onClick={() => setActivePage(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <button
          type="button"
          className={
            activePage === "settings"
              ? "nav-item active settings-button"
              : "nav-item settings-button"
          }
          onClick={() => setActivePage("settings")}
        >
          Settings
        </button>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="eyebrow">LifeOS</span>
            <h2>{navigation.find((item) => item.id === activePage)?.label ?? "Settings"}</h2>
          </div>

          <div className="profile">
            <span className="profile-name">Aditya</span>
          </div>
        </header>

        <div className="page-content">
          <PageContent page={activePage} />
        </div>
      </main>
    </div>
  );
}
