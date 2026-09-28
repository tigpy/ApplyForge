import { ApplicationsTable } from "../components/ApplicationsTable";
import { ErrorNote } from "../components/Layout";
import { useAsync } from "../hooks/useAsync";
import { api } from "../services/api";

export default function Applications() {
  const { data, error } = useAsync(api.listApplications);
  return (
    <>
      <h1 className="text-xl font-bold">Application History</h1>
      <ErrorNote message={error} />
      <ApplicationsTable applications={data ?? []} />
    </>
  );
}
