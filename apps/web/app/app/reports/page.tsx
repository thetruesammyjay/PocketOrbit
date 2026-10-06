import Link from "next/link";

import { PageHeading } from "@/components/page-heading";

export default function ReportsPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
  return <><PageHeading title="Reports" description="Export a clearly labeled sample holdings file." /><section className="panel content-panel"><h2>Sample holdings CSV</h2><p>This download contains the same illustrative values used on the dashboard. It is not an account statement.</p><Link className="button button--secondary" href={`${apiUrl}/reports/demo/holdings.csv`}>Download sample CSV</Link></section></>;
}
