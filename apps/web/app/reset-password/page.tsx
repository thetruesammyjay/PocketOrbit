import Link from "next/link";
import { AccountActionForm } from "@/features/auth/account-action-form";

export default function ResetPasswordPage() {
  return <main className="auth-layout"><section className="panel auth-card"><Link className="brand-lockup" href="/"><span className="brand-mark">PO</span><span>PocketOrbit</span></Link><h1>Choose a new password</h1><p className="muted">Reset links expire after 30 minutes and work once.</p><AccountActionForm mode="reset" /></section></main>;
}
