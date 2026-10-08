import Link from "next/link";
import { AccountActionForm } from "@/features/auth/account-action-form";

export default function VerifyEmailPage() {
  return <main className="auth-layout"><section className="panel auth-card"><Link className="brand-lockup" href="/"><span className="brand-mark">PO</span><span>PocketOrbit</span></Link><h1>Verify your email</h1><p className="muted">Use the link in your inbox, or request a fresh one.</p><AccountActionForm mode="verify" /></section></main>;
}
