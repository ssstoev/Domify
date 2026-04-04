import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import ListingCard, { type Listing } from "./ListingCard";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  listings?: Listing[];
}

const SUGGESTED_QUERIES = [
  "Show apartments under €100k in Old Town",
  "Find 3-bedroom houses near the coast",
  "Is this listing underpriced compared to neighbors?",
  "What's the average price per m² in Centro?",
];

const MOCK_LISTINGS: Listing[] = [
  {
    id: "1",
    title: "Bright Studio Apartment with Terrace",
    price: 78000,
    currency: "EUR",
    location: "Málaga",
    neighborhood: "El Palo",
    bedrooms: 1,
    bathrooms: 1,
    area: 45,
    imageUrl: "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&h=300&fit=crop",
    url: "#",
    tags: ["Underpriced", "Near beach"],
  },
  {
    id: "2",
    title: "Renovated Flat in Historic Center",
    price: 92000,
    currency: "EUR",
    location: "Málaga",
    neighborhood: "Centro",
    bedrooms: 2,
    bathrooms: 1,
    area: 62,
    imageUrl: "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400&h=300&fit=crop",
    url: "#",
    tags: ["Recently renovated"],
  },
  {
    id: "3",
    title: "Cozy Ground Floor with Patio",
    price: 85000,
    currency: "EUR",
    location: "Málaga",
    neighborhood: "El Palo",
    bedrooms: 2,
    bathrooms: 1,
    area: 55,
    imageUrl: "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400&h=300&fit=crop",
    url: "#",
    tags: ["Garden", "Pet friendly"],
  },
];

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: messageText,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Simulate AI response with mock data
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `I found **3 listings** matching your query in the area. Here are the best matches sorted by value:`,
        listings: MOCK_LISTINGS,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1200);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header */}
      <header className="flex items-center gap-3 border-b border-border px-6 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
          <Building2 className="h-5 w-5 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-foreground">EstateQuery</h1>
          <p className="text-xs text-muted-foreground">
            AI-powered real estate search
          </p>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="mx-auto max-w-2xl space-y-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center py-16 text-center">
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-secondary">
                <Sparkles className="h-8 w-8 text-primary" />
              </div>
              <h2 className="mb-2 text-xl font-semibold text-foreground">
                Ask me about real estate
              </h2>
              <p className="mb-8 max-w-md text-sm text-muted-foreground">
                Search listings, compare prices, analyze neighborhoods, or paste
                a listing URL to get insights.
              </p>
              <div className="grid w-full max-w-lg grid-cols-1 gap-2 sm:grid-cols-2">
                {SUGGESTED_QUERIES.map((query) => (
                  <button
                    key={query}
                    onClick={() => handleSend(query)}
                    className="rounded-xl border border-border bg-card px-4 py-3 text-left text-sm text-foreground transition-colors hover:border-primary hover:bg-secondary"
                  >
                    {query}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] space-y-3 ${
                  message.role === "user"
                    ? "rounded-2xl rounded-br-md bg-chat-user px-4 py-3 text-chat-user-foreground"
                    : ""
                }`}
              >
                <p className={`text-sm leading-relaxed ${message.role === "assistant" ? "text-foreground" : ""}`}>
                  {message.content.split("**").map((part, i) =>
                    i % 2 === 1 ? (
                      <strong key={i}>{part}</strong>
                    ) : (
                      <span key={i}>{part}</span>
                    )
                  )}
                </p>
                {message.listings && (
                  <div className="space-y-2">
                    {message.listings.map((listing) => (
                      <ListingCard key={listing.id} listing={listing} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-center gap-1.5 rounded-2xl bg-chat-assistant px-4 py-3">
                <div className="h-2 w-2 animate-pulse rounded-full bg-primary" />
                <div className="h-2 w-2 animate-pulse rounded-full bg-primary [animation-delay:150ms]" />
                <div className="h-2 w-2 animate-pulse rounded-full bg-primary [animation-delay:300ms]" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-border px-4 py-4">
        <div className="mx-auto flex max-w-2xl items-end gap-2">
          <div className="flex-1 rounded-xl border border-border bg-card px-4 py-3 focus-within:border-primary focus-within:ring-1 focus-within:ring-primary">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about real estate listings..."
              rows={1}
              className="w-full resize-none bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
            />
          </div>
          <Button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            size="icon"
            className="h-11 w-11 rounded-xl"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
