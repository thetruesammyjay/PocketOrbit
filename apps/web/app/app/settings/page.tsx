import { PageHeading } from "@/components/page-heading";

export default function SettingsPage() {
  return <><PageHeading title="Settings" description="Portfolio preferences will be saved here once accounts are configured." /><section className="panel content-panel"><h2>Reporting currency</h2><p>Reporting currency changes displayed values, not the underlying asset quantities.</p><div className="form-field"><label htmlFor="currency">Preferred currency</label><select id="currency" disabled defaultValue="USD"><option value="USD">USD · US Dollar</option><option value="EUR">EUR · Euro</option><option value="GBP">GBP · Pound Sterling</option></select><span className="form-help">Preferences are not saved in this scaffold.</span></div></section></>;
}
