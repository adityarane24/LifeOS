import { useEffect, useState } from "react";
import { getUserAnalytics } from "../api/analytics";
import type { UserAnalytics } from "../types/analytics";

const USER_ID = "6ed7310b-a6d5-4b55-b656-af1726c62572";

export default function ApiTest() {
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const end = new Date();
        const start = new Date();

        start.setDate(start.getDate() - 30);

        const data = await getUserAnalytics(
          USER_ID,
          start.toISOString(),
          end.toISOString(),
        );

        setAnalytics(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to connect to the LifeOS API.",
        );
      } finally {
        setLoading(false);
      }
    }

    loadAnalytics();
  }, []);

  if (loading) {
    return <h1>Loading LifeOS analytics...</h1>;
  }

  if (error) {
    return (
      <div>
        <h1>LifeOS API Connection Test</h1>
        <p>Connection failed.</p>
        <pre>{error}</pre>
      </div>
    );
  }

  return (
    <div>
      <h1>LifeOS API Connection Test</h1>

      <p>Frontend → Backend connection successful.</p>

      <h2>Analytics</h2>

      <pre>{JSON.stringify(analytics, null, 2)}</pre>
    </div>
  );
}
