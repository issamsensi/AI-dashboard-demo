import { ChatPanel } from '../components/ChatPanel';

export function AssistantPage() {
  return (
    <div className="pb-10">
      <ChatPanel
        title="AI Shopping Assistant"
        description="Ask for searches, comparisons, product explanations, and budget-friendly recommendations. The assistant only uses SQLite-backed tools."
        endpoint="customer"
        examples={[
          'Show me the best laptops under $1500',
          'Compare products 1 and 2',
          'What categories do you have?',
          'Recommend a good phone under $800',
        ]}
      />
    </div>
  );
}
