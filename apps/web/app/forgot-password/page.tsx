import Link from "next/link";
import { AccountActionForm } from "@/features/auth/account-action-form";

export default function ForgotPasswordPage() {
  return <main className="auth-layout"><section className="panel auth-card"><Link className="brand-lockup" href="/"><span className="brand-mark">PO</span><span>PocketOrbit</span></Link><h1>Reset your password</h1><p className="muted">We’ll send a one-time reset link if an account matches that email.</p><AccountActionForm mode="forgot" /></section></main>;
}
