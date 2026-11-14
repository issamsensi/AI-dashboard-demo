import { useMemo, useState } from 'react';
import { Bot, LoaderCircle, SendHorizonal, Sparkles } from 'lucide-react';
import type { ChatMessage } from '../lib/types';
import { sendAdminChat, sendCustomerChat } from '../lib/api';

function cx(...parts: Array<string | false | undefined>) {
  return parts.filter(Boolean).join(' ');
}

export function ChatPanel({
  title,
  description,
  endpoint,
  accent = 'accent',
  examples,
}: {
  title: string;
  description: string;
  endpoint: 'customer' | 'admin';
  accent?: 'accent' | 'slate';
  examples: string[];
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: description },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (message: string) => {
    if (!message.trim() || loading) return;
    const nextMessages: ChatMessage[] = [...messages, { role: 'user', content: message.trim() }];
    setMessages(nextMessages);
    setInput('');
    setLoading(true);
    try {
      const response =
        endpoint === 'customer'
          ? await sendCustomerChat(message, messages)
          : await sendAdminChat(message, messages);
      setMessages([...nextMessages, { role: 'assistant', content: response.answer }]);
    } catch (error) {
      setMessages([...nextMessages, { role: 'assistant', content: 'The SQLite-backed assistant could not complete that request right now.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="glass flex h-full min-h-[700px] flex-col overflow-hidden rounded-[2rem] shadow-xl shadow-black/5">
      <div className={cx('border-b border-[var(--border)] px-6 py-5', accent === 'accent' ? 'bg-accent-600 text-white' : 'bg-slate-900 text-white dark:bg-white dark:text-slate-900')}>
        <div className="flex items-center gap-3">
          <div className={cx('rounded-2xl p-2', accent === 'accent' ? 'bg-white/15' : 'bg-black/10')}>
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-2xl font-display font-bold">{title}</h2>
            <p className={cx('text-sm', accent === 'accent' ? 'text-white/80' : 'text-white/70 dark:text-slate-600')}>
              {description}
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-6">
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={cx(
              'max-w-[88%] rounded-3xl px-4 py-3 text-sm leading-6 shadow-sm',
              message.role === 'user'
                ? 'ml-auto bg-accent-600 text-white'
                : 'bg-white/90 text-slate-900 dark:bg-white/5 dark:text-slate-100',
            )}
          >
            {message.content}
          </div>
        ))}
        {loading && (
          <div className="inline-flex items-center gap-2 rounded-3xl bg-white/90 px-4 py-3 text-sm text-[var(--muted)] dark:bg-white/5">
            <LoaderCircle className="h-4 w-4 animate-spin" />
            Querying SQLite and AI tools...
          </div>
        )}
      </div>

      <div className="border-t border-[var(--border)] p-5">
        <div className="mb-3 flex flex-wrap gap-2">
          {examples.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => setInput(example)}
              className="rounded-full bg-slate-900/5 px-3 py-2 text-xs font-semibold text-slate-700 transition hover:bg-accent-600 hover:text-white dark:bg-white/10 dark:text-slate-200"
            >
              <Sparkles className="mr-1 inline h-3 w-3" />
              {example}
            </button>
          ))}
        </div>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            void submit(input);
          }}
          className="flex gap-3"
        >
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask about products, comparisons, budgets, stock, or sales..."
            className="min-w-0 flex-1 rounded-2xl border border-[var(--border)] bg-white/80 px-4 py-3 text-sm outline-none transition placeholder:text-[var(--muted)] focus:border-accent-600 dark:bg-white/5"
          />
          <button
            type="submit"
            className="inline-flex items-center gap-2 rounded-2xl bg-accent-600 px-5 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 disabled:opacity-60"
            disabled={loading}
          >
            <SendHorizonal className="h-4 w-4" />
            Send
          </button>
        </form>
      </div>
    </section>
  );
}
