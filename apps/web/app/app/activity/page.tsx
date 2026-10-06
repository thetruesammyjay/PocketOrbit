import { Card } from "@pocketorbit/ui";

import { PageHeading } from "@/components/page-heading";
import { ActivityList } from "@/features/activity/activity-list";
import { getPortfolioSummary } from "@/features/portfolio/portfolio-api";

export default async function ActivityPage() {
  const portfolio = await getPortfolioSummary();
  return <><PageHeading title="Activity" description="Supported activity records, grouped in plain language." /><div className="demo-banner"><span aria-hidden="true">i</span><div><strong>Sample activity</strong>These records are examples. No live wallet history has been retrieved.</div></div><Card><div className="panel-heading"><div><h2>Recent records</h2><p>Source names stay attached to each item</p></div></div><ActivityList items={portfolio.activity} /></Card></>;
}
