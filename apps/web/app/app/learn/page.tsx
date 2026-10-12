import { LearnQuest } from "@/features/learn/learn-quest";

import { FeaturePage } from "@/components/feature-page";

export default function AppLearnPage() {
  return (
    <FeaturePage
      title="Learn"
      description="Play a quick round, sharpen your portfolio instincts, and learn what each number can tell you."
    >
      <LearnQuest />
    </FeaturePage>
  );
}
