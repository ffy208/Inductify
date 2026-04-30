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
const USER_AVATAR = "https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatars/3a906b3de8eaa53e14582edf5c918b5d.jpg";

const WELCOME: ChatMsg = {
  id: "welcome",
  role: "assistant",
  content: "Hi! I'm the Inductify onboarding assistant. Ask me anything about company policies, benefits, or procedures — I'll cite the source documents.",
};

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
  const sessionId = useRef<string>(crypto.randomUUID());
  const bottomRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom whenever messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({behavior: "smooth"});
  }, [messages]);

  const handleSend = useCallback(async (message: string) => {
    if (isAsking) return;

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
    await api.deleteSession(sessionId.current).catch(() => {});
    sessionId.current = crypto.randomUUID();
    setMessages([WELCOME]);
    setUploadState({phase: "idle"});
  }, []);

  return (
    <div className="h-dvh w-full max-w-full">
      <SidebarContainer
        header={
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
        }
        subTitle="RAG-powered onboarding"
        title="Inductify Assistant"
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
