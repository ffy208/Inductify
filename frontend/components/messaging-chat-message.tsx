"use client";
import type {MessagingChatMessageProps, Source} from "./data";

import React, {useCallback, useState} from "react";
import {Avatar, Image, Chip} from "@heroui/react";
import {Icon} from "@iconify/react";
import {cn} from "@heroui/react";

// ---------------------------------------------------------------------------
// Source citation card
// ---------------------------------------------------------------------------

function fileIcon(filename: string): string {
  const ext = filename.split(".").pop()?.toLowerCase();
  switch (ext) {
    case "pdf":  return "solar:file-text-bold";
    case "xlsx": return "solar:file-bold";
    case "md":   return "solar:file-bold";
    default:     return "solar:document-bold";
  }
}

function SourceCard({source, index}: {source: Source; index: number}) {
  const [expanded, setExpanded] = useState(false);
  const shortName = source.filename.split("/").pop() ?? source.filename;

  return (
    <button
      className={cn(
        "flex flex-col gap-1 rounded-lg border border-default-200 bg-default-50",
        "px-3 py-2 text-left transition-all duration-150",
        "hover:border-primary-300 hover:bg-primary-50/30 focus:outline-none",
        "min-w-[180px] max-w-[220px] flex-shrink-0",
      )}
      type="button"
      onClick={() => setExpanded((v) => !v)}
    >
      <div className="flex items-center gap-1.5">
        <Icon
          className="flex-shrink-0 text-primary-400"
          icon={fileIcon(shortName)}
          width={13}
        />
        <span className="truncate text-[11px] font-semibold text-default-600">{shortName}</span>
        {source.score != null && (
          <Chip
            className="ml-auto flex-shrink-0"
            color="primary"
            size="sm"
            variant="flat"
            classNames={{base: "h-4 px-1", content: "text-[10px] font-mono px-0"}}
          >
            {source.score.toFixed(2)}
          </Chip>
        )}
      </div>
      <p
        className={cn(
          "text-[11px] leading-relaxed text-default-500",
          expanded ? "" : "line-clamp-2",
        )}
      >
        {source.excerpt}
      </p>
      <span className="text-[10px] text-default-300">
        {expanded ? "collapse ↑" : "expand ↓"} · chunk {index}
      </span>
    </button>
  );
}

// ---------------------------------------------------------------------------
// Loading shimmer
// ---------------------------------------------------------------------------

function LoadingDots() {
  return (
    <div className="flex items-center gap-1 py-1">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="block h-2 w-2 animate-bounce rounded-full bg-default-400"
          style={{animationDelay: `${i * 0.15}s`}}
        />
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

const MessagingChatMessage = React.forwardRef<HTMLDivElement, MessagingChatMessageProps>(
  ({avatar, name, time, message, isRTL, imageUrl, sources, isLoading, className, classNames, ...props}, ref) => {
    const MessageAvatar = useCallback(
      () => (
        <div className="relative flex-none">
          <Avatar src={avatar} />
        </div>
      ),
      [avatar],
    );

    const Message = () => (
      <div className="flex max-w-[70%] flex-col gap-2">
        <div
          className={cn(
            "relative w-full rounded-medium bg-content2 px-4 py-3 text-default-600",
            classNames?.base,
          )}
        >
          <div className="flex">
            <div className="w-full text-small font-semibold text-default-foreground">{name}</div>
            {time && <div className="flex-end text-small text-default-400">{time}</div>}
          </div>
          <div className="mt-2 text-small text-default-900">
            {isLoading ? (
              <LoadingDots />
            ) : (
              <>
                <div className="whitespace-pre-line">{message}</div>
                {imageUrl && (
                  <Image
                    alt={`Image sent by ${name}`}
                    className="mt-2 border-2 border-default-200 shadow-small"
                    height={96}
                    src={imageUrl}
                    width={264}
                  />
                )}
              </>
            )}
          </div>
        </div>

        {/* Source citation cards */}
        {sources && sources.length > 0 && !isLoading && (
          <div className="flex flex-col gap-1">
            <p className="px-1 text-[10px] font-medium uppercase tracking-wider text-default-400">
              Sources
            </p>
            <div className="flex gap-2 overflow-x-auto pb-1">
              {sources.map((src, i) => (
                <SourceCard key={`${src.filename}-${i}`} index={src.chunk_index} source={src} />
              ))}
            </div>
          </div>
        )}
      </div>
    );

    return (
      <div
        {...props}
        ref={ref}
        className={cn("flex gap-3", {"flex-row-reverse": isRTL}, className)}
      >
        <MessageAvatar />
        <Message />
      </div>
    );
  },
);

MessagingChatMessage.displayName = "MessagingChatMessage";

export default MessagingChatMessage;
