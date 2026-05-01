"use client";

import type {Source} from "../lib/api";

import React, {useCallback, useEffect, useRef, useState} from "react";
import {
  ScrollShadow,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownSection,
  DropdownItem,
  Button,
  Chip,
} from "@heroui/react";
import {Icon} from "@iconify/react";

import SidebarContainer from "./sidebar-with-chat-history";
import MessagingChatMessage from "./messaging-chat-message";
import PromptInputWithEnclosedActions from "./prompt-input-with-enclosed-actions";
import {ThemeSwitch} from "./theme-switch";
import * as api from "../lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ChatMsg {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  isLoading?: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMsg[];
}

type UploadState =
  | {phase: "idle"}
  | {phase: "uploading"}
  | {phase: "indexing"; jobId: string}
  | {phase: "done"; chunks: number}
  | {phase: "error"; message: string};

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BOT_AVATAR = "https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png";
const USER_AVATAR = "/YahaUsagi.webp";

const WELCOME: ChatMsg = {
  id: "welcome",
  role: "assistant",
  content: "Hi! I'm the Inductify onboarding assistant. Ask me anything about company policies, benefits, or procedures — I'll cite the source documents.",
};

// ---------------------------------------------------------------------------
// Demo conversations — seeded for demo profile
// ---------------------------------------------------------------------------

const src = (filename: string, excerpt: string, score = 0.91): Source => ({
  filename,
  chunk_index: 0,
  excerpt,
  score,
});

const DEMO_CONVERSATIONS: Conversation[] = [
  {
    id: "demo-pto",
    title: "PTO Policy & Accrual",
    messages: [
      WELCOME,
      {id: "d1u1", role: "user", content: "How many vacation days do I get per year?"},
      {
        id: "d1a1",
        role: "assistant",
        content:
          "Full-time employees accrue **15 vacation days per year** (1.25 days/month), increasing to **20 days** after 3 years of continuous service. Requests for a single day require 2 business days' notice; blocks of 5+ days need 2 weeks' notice submitted via the HR portal.\n\nThere are also **10 paid holidays** and **5 sick days** annually — sick days do not roll over.",
        sources: [
          src("p_002481_employee_handbook.txt", "Full-time employees accrue 1.25 vacation days per calendar month (15 days/year). After 36 months of continuous service, accrual increases to 1.67 days/month (20 days/year)."),
          src("p_003083_pto_policy.md", "Company recognizes 10 federal and company-designated holidays. Sick leave of 5 days per year is provided separately from vacation accrual and does not carry over.", 0.87),
        ],
      },
      {id: "d1u2", role: "user", content: "Can unused PTO roll over?"},
      {
        id: "d1a2",
        role: "assistant",
        content:
          "Yes — **up to 5 unused vacation days** roll over into the following calendar year. Any balance above 5 days is forfeited on December 31st. If your employment ends, accrued vacation up to the rollover cap is paid out in your final paycheck.",
        sources: [
          src("p_002481_employee_handbook.txt", "Maximum PTO rollover is 5 days per year. Balances exceeding 5 days are forfeited at year-end. Accrued unused vacation (up to rollover maximum) is paid upon separation.", 0.94),
        ],
      },
    ],
  },
  {
    id: "demo-remote",
    title: "Remote Work Policy",
    messages: [
      WELCOME,
      {id: "d2u1", role: "user", content: "What's the work-from-home policy?"},
      {
        id: "d2a1",
        role: "assistant",
        content:
          "Employees may work remotely **up to 3 days per week** after completing their 90-day onboarding period. The two anchor days (Tuesday and Thursday) require in-office presence unless a manager grants an exception.\n\nRemote work requires a stable internet connection of at least 25 Mbps and a private workspace. IT will provide a VPN token and laptop within your first week.",
        sources: [
          src("p_004711_remote_work_policy.xlsx", "Eligible employees may work remotely up to 3 days/week post-90-day probation. In-office anchor days: Tuesday and Thursday. Manager exceptions require written approval.", 0.96),
          src("p_001665_it_access_policy.pdf", "Remote employees must connect via company VPN. Minimum home internet speed: 25 Mbps download. IT issues VPN credentials within 5 business days of start date.", 0.88),
        ],
      },
      {id: "d2u2", role: "user", content: "What about international remote work?"},
      {
        id: "d2a2",
        role: "assistant",
        content:
          "International remote work is permitted for **up to 30 consecutive days** per calendar year, subject to prior approval from your manager and HR. Tax and visa compliance is the employee's responsibility. Stays exceeding 30 days require a formal global mobility review.",
        sources: [
          src("p_004711_remote_work_policy.xlsx", "International remote work allowed up to 30 consecutive days/year with manager and HR approval. Employee is responsible for local tax and work-permit compliance.", 0.92),
        ],
      },
    ],
  },
  {
    id: "demo-expense",
    title: "Expense Reimbursement Limits",
    messages: [
      WELCOME,
      {id: "d3u1", role: "user", content: "What's the limit for business meal expenses?"},
      {
        id: "d3a1",
        role: "assistant",
        content:
          "Business meal reimbursement limits:\n- **Individual lunch** (client or team): up to **$35 per person**\n- **Client dinner**: up to **$75 per person**\n- **Team celebration meals**: up to **$50 per person**, pre-approved by a VP or above\n\nAll meals must include a receipt and a list of attendees with business purpose noted in Expensify.",
        sources: [
          src("p_005359_expense_policy.pdf", "Meal reimbursement per-person limits: business lunch $35, client dinner $75, team celebration $50 (VP pre-approval required). Receipts mandatory; itemize attendees and business purpose.", 0.97),
        ],
      },
      {id: "d3u2", role: "user", content: "What about travel expenses — flights and hotels?"},
      {
        id: "d3a2",
        role: "assistant",
        content:
          "For domestic travel:\n- **Flights**: economy class only; book at least 14 days in advance when possible\n- **Hotels**: up to **$250/night** in major metro areas, **$175/night** elsewhere\n- **Ground transport**: Uber/Lyft/taxi receipts required; personal vehicle reimbursed at the current IRS rate (**$0.67/mile**)\n\nSubmit all expenses in Expensify within **30 days** of the trip.",
        sources: [
          src("p_005359_expense_policy.pdf", "Domestic flights: economy. Hotels: $250/night (metro) or $175/night (other). Ground: receipt required; mileage at IRS standard rate. Expense submission deadline: 30 days post-trip.", 0.95),
          src("p_005365_travel_guidelines.pdf", "Book flights at least 14 days in advance. Upgrades to business class require VP approval and are reimbursed only for flights over 6 hours.", 0.83),
        ],
      },
    ],
  },
  {
    id: "demo-benefits",
    title: "Health Benefits Enrollment",
    messages: [
      WELCOME,
      {id: "d4u1", role: "user", content: "When can I enroll in health insurance?"},
      {
        id: "d4a1",
        role: "assistant",
        content:
          "New employees have a **30-day enrollment window** starting from their first day. You can choose from three plans:\n\n1. **PPO Plus** — highest coverage, higher premium\n2. **HDHP + HSA** — lower premium, $1,500 employer HSA contribution annually\n3. **HMO Select** — network-only, lowest premium\n\nCoverage begins on the **1st of the month following your start date** (or immediately if you start on the 1st). Miss the window and you must wait for Open Enrollment in November.",
        sources: [
          src("p_004341_benefits_guide.xlsx", "New hire enrollment window: 30 days from start date. Plan options: PPO Plus, HDHP+HSA ($1,500 employer contribution), HMO Select. Coverage effective date: 1st of following month.", 0.98),
        ],
      },
      {id: "d4u2", role: "user", content: "Does the company cover dental and vision too?"},
      {
        id: "d4a2",
        role: "assistant",
        content:
          "Yes. Both dental and vision are included in the benefits package:\n\n- **Dental**: 100% coverage for preventive care (cleanings, X-rays), 80% for basic restorative, 50% for major restorative (crowns, root canals). Annual maximum: **$2,000**.\n- **Vision**: annual eye exam covered 100%; up to **$200** toward frames/contacts per year.\n\nBoth plans enroll on the same 30-day window as medical.",
        sources: [
          src("p_004341_benefits_guide.xlsx", "Dental: 100% preventive, 80% basic restorative, 50% major restorative; $2,000 annual max. Vision: 100% exam, $200 frames/contacts allowance per year.", 0.96),
        ],
      },
    ],
  },
  {
    id: "demo-perf",
    title: "Performance Review Cycle",
    messages: [
      WELCOME,
      {id: "d5u1", role: "user", content: "When is the performance review? How does it work?"},
      {
        id: "d5a1",
        role: "assistant",
        content:
          "The company runs a **twice-yearly review cycle**:\n\n- **Mid-Year Check-In** (June): developmental focus — no rating, no comp impact. Manager and employee discuss progress against goals.\n- **Annual Review** (November): formal rating on a 5-point scale. Results feed into year-end compensation adjustments effective January 1st.\n\nNew employees on probation (first 90 days) have a **90-day review** with their manager before joining the main cycle.",
        sources: [
          src("p_003203_performance_management.md", "Review cycles: mid-year (June, developmental only) and annual (November, rated 1–5). Year-end compensation changes effective Jan 1. New hires: 90-day review before joining main cycle.", 0.95),
        ],
      },
      {id: "d5u2", role: "user", content: "How is the performance bonus calculated?"},
      {
        id: "d5a2",
        role: "assistant",
        content:
          "Annual bonuses are based on a combination of individual rating and company performance multiplier:\n\n| Rating | Target Bonus % of Base |\n|--------|------------------------|\n| 5 – Exceptional | 20% |\n| 4 – Exceeds | 15% |\n| 3 – Meets | 10% |\n| 2 – Developing | 5% |\n| 1 – Below | 0% |\n\nThe final payout = (target %) × (company performance multiplier, 0.5x–1.5x). Bonuses are paid in **February** following the review year.",
        sources: [
          src("p_003203_performance_management.md", "Bonus target percentages: Exceptional 20%, Exceeds 15%, Meets 10%, Developing 5%, Below 0%. Final bonus = target × company multiplier (0.5–1.5). Payment month: February.", 0.97),
          src("p_004523_compensation_policy.md", "Company performance multiplier is determined by the Board in January based on revenue, EBITDA, and OKR attainment. HR communicates multiplier to managers before February payroll.", 0.89),
        ],
      },
    ],
  },
  {
    id: "demo-it",
    title: "IT Equipment & VPN Access",
    messages: [
      WELCOME,
      {id: "d6u1", role: "user", content: "How do I get my laptop and VPN access on day one?"},
      {
        id: "d6a1",
        role: "assistant",
        content:
          "IT onboarding is handled automatically once HR finalises your start date:\n\n1. **Laptop** — shipped to your address (or available for pickup at the office) the business day before your start. Standard issue is a 14\" MacBook Pro (M-series) or a Dell XPS 15 (Windows) based on team preference.\n2. **VPN** — a Cisco AnyConnect token and setup guide are emailed to your personal address on Day 1 morning. First-time setup takes ~10 minutes.\n3. **SSO / email** — Google Workspace account provisioned automatically; credentials arrive via your personal email by 8 AM on Day 1.\n\nIf anything is missing, contact IT at **it-help@company.com** or Slack `#it-support`.",
        sources: [
          src("p_001665_it_access_policy.pdf", "Hardware shipped D-1 before start date. Standard: 14\" MacBook Pro (M-series) or Dell XPS 15. VPN (Cisco AnyConnect) credentials emailed Day 1. Google Workspace SSO auto-provisioned.", 0.96),
          src("p_001836_it_onboarding_checklist.txt", "IT support contact: it-help@company.com and Slack #it-support. Missing equipment or access issues must be reported within 48 hours of start date.", 0.88),
        ],
      },
    ],
  },
  {
    id: "demo-parental",
    title: "Parental Leave Policy",
    messages: [
      WELCOME,
      {id: "d7u1", role: "user", content: "What parental leave does the company offer?"},
      {
        id: "d7a1",
        role: "assistant",
        content:
          "The company provides **fully paid parental leave** for all parents:\n\n- **Primary caregiver** (birth, adoption, surrogacy): **16 weeks** paid at 100% base salary\n- **Secondary caregiver**: **6 weeks** paid at 100% base salary\n- Employees must have completed **6 months of service** to be eligible\n- Leave can be taken any time within **12 months** of the child's birth/placement\n\nLeave may be taken all at once or split into two blocks (minimum 2-week blocks). Notify HR at least **8 weeks** before the expected start.",
        sources: [
          src("p_004972_parental_leave_policy.txt", "Primary caregiver leave: 16 weeks fully paid. Secondary caregiver: 6 weeks fully paid. Eligibility: 6 months tenure. Leave window: 12 months from birth/placement. Minimum block: 2 weeks.", 0.98),
          src("p_004972_parental_leave_policy.txt", "Notification requirement: inform HR a minimum of 8 weeks before leave start date. FMLA runs concurrently where applicable.", 0.93),
        ],
      },
    ],
  },
  {
    id: "demo-coc",
    title: "Code of Conduct — Key Points",
    messages: [
      WELCOME,
      {id: "d8u1", role: "user", content: "What are the main points of the code of conduct I should know as a new employee?"},
      {
        id: "d8a1",
        role: "assistant",
        content:
          "The Code of Conduct covers five core areas:\n\n1. **Conflicts of interest** — disclose any financial interest in a competitor or supplier to your manager and Legal within 30 days of joining or when a conflict arises.\n2. **Confidentiality** — company data, customer data, and trade secrets must not be shared externally without a signed NDA on file.\n3. **Anti-harassment** — zero tolerance for harassment or discrimination based on any protected characteristic. Report incidents to HR or via the anonymous hotline.\n4. **Social media** — do not post about unreleased products or financials. Add a disclaimer when sharing opinions professionally.\n5. **Gifts & entertainment** — accept nothing valued over **$50** from vendors or clients without manager approval.\n\nAll employees sign the CoC annually. Violations may result in termination.",
        sources: [
          src("p_000235_code_of_conduct.pdf", "Five pillars: conflicts of interest (disclose within 30 days), confidentiality, anti-harassment (zero tolerance), social media conduct, gifts & entertainment ($50 limit). Annual re-signature required.", 0.97),
          src("p_000296_ethics_policy.txt", "Anonymous ethics reporting hotline available 24/7. HR investigates all reports. Retaliation against reporters is a terminable offense.", 0.85),
        ],
      },
    ],
  },
];

// ---------------------------------------------------------------------------
// Upload status badge
// ---------------------------------------------------------------------------

function UploadBadge({state, onDismiss}: {state: UploadState; onDismiss: () => void}) {
  if (state.phase === "idle") return null;

  const configs: Record<Exclude<UploadState["phase"], "idle">, {color: "default" | "primary" | "success" | "danger"; icon: string; label: string}> = {
    uploading: {color: "primary",  icon: "solar:upload-linear",          label: "Uploading…"},
    indexing:  {color: "primary",  icon: "solar:refresh-linear",         label: "Indexing documents…"},
    done:      {color: "success",  icon: "solar:check-circle-bold",      label: state.phase === "done" ? `Indexed ${state.chunks} chunks` : ""},
    error:     {color: "danger",   icon: "solar:danger-triangle-bold",   label: state.phase === "error" ? state.message : ""},
  };

  const cfg = configs[state.phase as Exclude<UploadState["phase"], "idle">];

  return (
    <div className="flex items-center gap-2">
      <Chip
        color={cfg.color}
        size="sm"
        startContent={
          <Icon
            className={state.phase === "indexing" ? "animate-spin" : ""}
            icon={cfg.icon}
            width={14}
          />
        }
        variant="flat"
      >
        {cfg.label}
      </Chip>
      {(state.phase === "done" || state.phase === "error") && (
        <button className="text-default-300 hover:text-default-500" type="button" onClick={onDismiss}>
          <Icon icon="solar:close-circle-linear" width={14} />
        </button>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------

export default function App() {
  const [messages, setMessages] = useState<ChatMsg[]>([WELCOME]);
  const [isAsking, setIsAsking] = useState(false);
  const [uploadState, setUploadState] = useState<UploadState>({phase: "idle"});
  const [conversations, setConversations] = useState<Conversation[]>(DEMO_CONVERSATIONS);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const sessionId = useRef<string>(crypto.randomUUID());
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({behavior: "smooth"});
  }, [messages]);

  const handleSelectConversation = useCallback((id: string) => {
    // Auto-save the current unsaved conversation before switching away
    const userMsgs = messages.filter((m) => m.role === "user");
    if (userMsgs.length > 0 && activeConvId === null) {
      const title = userMsgs[0].content.slice(0, 42) + (userMsgs[0].content.length > 42 ? "…" : "");
      const sid = sessionId.current;
      setConversations((prev) => {
        if (prev.some((c) => c.id === sid)) return prev; // already saved
        return [{id: sid, title, messages: [...messages]}, ...prev];
      });
    }
    const conv = conversations.find((c) => c.id === id);
    if (conv) {
      setMessages(conv.messages);
      setActiveConvId(id);
    }
  }, [messages, activeConvId, conversations]);

  const handleSend = useCallback(async (message: string) => {
    if (isAsking) return;

    // Detach from any demo conversation as soon as the user types their own message
    setActiveConvId(null);

    const userMsg: ChatMsg = {id: crypto.randomUUID(), role: "user", content: message};
    const loadingMsg: ChatMsg = {id: "loading", role: "assistant", content: "", isLoading: true};

    setMessages((prev) => [...prev, userMsg, loadingMsg]);
    setIsAsking(true);

    try {
      const response = await api.ask(sessionId.current, message);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === "loading"
            ? {id: crypto.randomUUID(), role: "assistant", content: response.answer, sources: response.sources}
            : m,
        ),
      );
    } catch (err) {
      const errorText = err instanceof Error ? err.message : "Something went wrong. Is the backend running?";
      setMessages((prev) =>
        prev.map((m) =>
          m.id === "loading"
            ? {id: crypto.randomUUID(), role: "assistant", content: `⚠ ${errorText}`}
            : m,
        ),
      );
    } finally {
      setIsAsking(false);
    }
  }, [isAsking]);

  const handleFilesSelected = useCallback(async (files: File[]) => {
    setUploadState({phase: "uploading"});
    try {
      const chunks = await api.uploadAndIndex(files, (status) => {
        if (status.status === "indexing") {
          setUploadState({phase: "indexing", jobId: status.job_id});
        }
      });
      setUploadState({phase: "done", chunks});
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Upload failed";
      setUploadState({phase: "error", message: msg});
    }
  }, []);

  const handleNewChat = useCallback(async () => {
    // Save current conversation if the user has sent at least one message and it's not a demo
    const userMsgs = messages.filter((m) => m.role === "user");
    if (userMsgs.length > 0 && activeConvId === null) {
      const title = userMsgs[0].content.slice(0, 42) + (userMsgs[0].content.length > 42 ? "…" : "");
      setConversations((prev) => [
        {id: sessionId.current, title, messages: [...messages]},
        ...prev,
      ]);
    }
    await api.deleteSession(sessionId.current).catch(() => {});
    sessionId.current = crypto.randomUUID();
    setMessages([WELCOME]);
    setActiveConvId(null);
    setUploadState({phase: "idle"});
  }, [messages, activeConvId]);

  return (
    <div className="h-dvh w-full max-w-full">
      <SidebarContainer
        activeConversationId={activeConvId}
        conversations={conversations}
        header={
          <div className="flex items-center gap-1">
            <Dropdown className="bg-content1">
              <DropdownTrigger>
                <Button
                  className="min-w-[120px] text-default-400"
                  endContent={
                    <Icon className="text-default-400" height={20} icon="solar:alt-arrow-down-linear" width={20} />
                  }
                  variant="light"
                >
                  Inductify
                </Button>
              </DropdownTrigger>
              <DropdownMenu aria-label="Options" className="px-0 py-[16px]" variant="faded">
                <DropdownSection title="Actions">
                  <DropdownItem
                    key="new-chat"
                    className="text-default-500 data-[hover=true]:text-default-500"
                    description="Clear history and start fresh"
                    startContent={<Icon className="text-default-400" icon="solar:chat-round-dots-linear" width={20} />}
                    onPress={handleNewChat}
                  >
                    New Chat
                  </DropdownItem>
                </DropdownSection>
              </DropdownMenu>
            </Dropdown>
            <ThemeSwitch />
          </div>
        }
        subTitle="RAG-powered onboarding"
        title="Inductify Assistant"
        onNewChat={handleNewChat}
        onSelectConversation={handleSelectConversation}
      >
        <div className="relative flex h-full flex-col">
          <ScrollShadow className="flex h-full max-h-[60vh] flex-col gap-6 overflow-y-auto p-6 pb-8">
            {messages.map((msg) => (
              <MessagingChatMessage
                key={msg.id}
                avatar={msg.role === "user" ? USER_AVATAR : BOT_AVATAR}
                classNames={{base: "bg-default-50"}}
                isLoading={msg.isLoading}
                isRTL={msg.role === "user"}
                message={msg.content}
                name={msg.role === "user" ? "You" : "Inductify AI"}
                sources={msg.sources}
              />
            ))}
            <div ref={bottomRef} />
          </ScrollShadow>

          <div className="mt-auto flex max-w-full flex-col gap-2 px-6">
            {uploadState.phase !== "idle" && (
              <div className="px-2">
                <UploadBadge state={uploadState} onDismiss={() => setUploadState({phase: "idle"})} />
              </div>
            )}
            <PromptInputWithEnclosedActions
              classNames={{
                button: "bg-default-foreground opacity-100 w-[30px] h-[30px] !min-w-[30px] self-center",
                buttonIcon: "text-background",
                input: "placeholder:text-default-500",
              }}
              isLoading={isAsking}
              placeholder="Ask about company policies, benefits, onboarding…"
              onFilesSelected={handleFilesSelected}
              onSend={handleSend}
            />
            <p className="px-2 text-center text-small font-medium leading-5 text-default-500">
              Inductify AI answers from indexed documents. Verify important details.
            </p>
          </div>
        </div>
      </SidebarContainer>
    </div>
  );
}
