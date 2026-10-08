import { PageHeading } from "@/components/page-heading";
import { DeleteAccountForm } from "@/features/auth/delete-account-form";

export default function SettingsPage() {
  return <><PageHeading title="Settings" description="Account and portfolio preferences." /><section className="panel content-panel"><h2>Reporting currency</h2><p>Reporting currency changes displayed values, not the underlying asset quantities.</p><div className="form-field"><label htmlFor="currency">Preferred currency</label><select id="currency" disabled defaultValue="USD"><option value="USD">USD · US Dollar</option><option value="EUR">EUR · Euro</option><option value="GBP">GBP · Pound Sterling</option></select><span className="form-help">Changing and saving reporting currency is not available yet.</span></div></section><section className="panel content-panel"><h2>Delete account</h2><p>This removes your active account, saved portfolios, connected wallet addresses, snapshots, and imports. Backup copies may remain until the service retention policy expires.</p><DeleteAccountForm /></section></>;
}
