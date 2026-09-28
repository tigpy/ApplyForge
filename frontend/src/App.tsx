import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import ApplicationDetail from "./pages/ApplicationDetail";
import Applications from "./pages/Applications";
import Dashboard from "./pages/Dashboard";
import JobDetail from "./pages/JobDetail";
import Jobs from "./pages/Jobs";
import Resumes from "./pages/Resumes";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="resumes" element={<Resumes />} />
        <Route path="jobs" element={<Jobs />} />
        <Route path="jobs/:id" element={<JobDetail />} />
        <Route path="applications" element={<Applications />} />
        <Route path="applications/:id" element={<ApplicationDetail />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
