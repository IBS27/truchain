import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

interface VerifyPlaceholderProps {
  videoId: number;
  videoTitle: string;
  onBack: () => void;
}

export function VerifyPlaceholder({ videoId, videoTitle, onBack }: VerifyPlaceholderProps) {
  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>AI Verification</CardTitle>
          <CardDescription>
            Verifying: {videoTitle}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold mb-2">AI Verification Coming Soon</h3>
            <p className="text-muted-foreground mb-6">
              This feature will use AI to match video clips against authenticated official videos
              on the blockchain, providing instant verification of authenticity.
            </p>
            <div className="bg-muted p-4 rounded-lg text-left space-y-2">
              <p className="text-sm font-medium">Planned Features:</p>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>Speech-to-text analysis</li>
                <li>Transcript matching against official videos</li>
                <li>Blockchain-verified source tracking</li>
                <li>Timestamp and context verification</li>
              </ul>
            </div>
          </div>

          <Button onClick={onBack} className="w-full">
            Back to Feed
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
