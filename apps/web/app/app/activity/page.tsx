import { Card } from "@pocketorbit/ui";

import { PageHeading } from "@/components/page-heading";
import { ActivityList } from "@/features/activity/activity-list";
import { ActivityReviewPanel } from "@/features/activity/activity-review-panel";
import { getPortfolioSummary } from "@/features/portfolio/portfolio-api";

export default async function ActivityPage() {
  const portfolio = await getPortfolioSummary();
  return <><PageHeading title="Activity" description="Imported records with source details, review, and cautious transfer matching." />{portfolio.isDemo && <div className="demo-banner"><span aria-hidden="true">i</span><div><strong>Sample activity</strong>These records are examples. No live wallet history has been retrieved.</div></div>}{portfolio.isDemo ? <Card><div className="panel-heading"><div><h2>Sample records</h2><p>Source names stay attached to each item</p></div></div>{portfolio.activity.length ? <ActivityList items={portfolio.activity} /> : <p className="empty-panel-copy">Transaction records from imported files will appear here.</p>}</Card> : <ActivityReviewPanel portfolioId={portfolio.id} items={portfolio.activity} />}</>;
}
