import {
  AdminDataPage,
  resolveAdminOffset,
  type AdminRouteProps
} from "@/components/admin-data-page";

export default async function UsersPage({ searchParams }: AdminRouteProps) {
  const offset = await resolveAdminOffset(searchParams);
  return (
    <AdminDataPage
      offset={offset}
      title="Users"
      description="Account registration and verification overview."
      endpoint="users"
      columns={[
        { key: "email", label: "Email" },
        { key: "emailVerified", label: "Verified" },
        { key: "portfolioCount", label: "Portfolios" },
        { key: "createdAt", label: "Joined" }
      ]}
    />
  );
}
