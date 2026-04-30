"use client";
import type {TextAreaProps} from "@heroui/react";

import React, {useRef} from "react";
import {Button, Tooltip} from "@heroui/react";
import {Icon} from "@iconify/react";
import {cn} from "@heroui/react";

import PromptInput from "./prompt-input";

const ALLOWED = ".txt,.md,.pdf,.xlsx";

interface PromptInputWithActionsProps extends TextAreaProps {
  classNames?: Record<"button" | "buttonIcon" | "input", string>;
  isLoading?: boolean;
  onSend?: (message: string) => void;
  onFilesSelected?: (files: File[]) => void;
}

export default function PromptInputWithEnclosedActions({
  isLoading = false,
  onSend,
  onFilesSelected,
  ...props
}: PromptInputWithActionsProps) {
  const [prompt, setPrompt] = React.useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    const trimmed = prompt.trim();
    if (!trimmed || isLoading) return;
    onSend?.(trimmed);
    setPrompt("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);
    if (files.length > 0) {
      onFilesSelected?.(files);
    }
    // reset so the same file can be re-selected
    e.target.value = "";
  };

  const canSend = !!prompt.trim() && !isLoading;

  return (
    <form
      className="flex w-full items-start gap-2"
      onSubmit={(e) => {
        e.preventDefault();
        handleSend();
      }}
    >
      <input
        ref={fileInputRef}
        accept={ALLOWED}
        className="hidden"
        multiple
        type="file"
        onChange={handleFileChange}
      />

      <PromptInput
        {...props}
        classNames={{
          innerWrapper: "items-center",
          input: cn(
            "text-medium data-[has-start-content=true]:ps-0 data-[has-start-content=true]:pe-0",
            props.classNames?.input,
          ),
        }}
        isDisabled={isLoading}
        value={prompt}
        onKeyDown={handleKeyDown}
        onValueChange={setPrompt}
        endContent={
          <div className="flex gap-2">
            {!prompt && !isLoading && (
              <Tooltip showArrow content="Speak">
                <Button isIconOnly radius="full" variant="light">
                  <Icon className="text-default-500" icon="solar:microphone-3-linear" width={20} />
                </Button>
              </Tooltip>
            )}
            <Tooltip showArrow content="Send message">
              <Button
                isIconOnly
                className={props?.classNames?.button ?? ""}
                color={canSend ? "primary" : "default"}
                isDisabled={!canSend}
                isLoading={isLoading}
                radius="full"
                type="submit"
                variant={canSend ? "solid" : "flat"}
              >
                {!isLoading && (
                  <Icon
                    className={cn(
                      "[&>path]:stroke-[2px]",
                      canSend ? "text-primary-foreground" : "text-default-500",
                      props?.classNames?.buttonIcon ?? "",
                    )}
                    icon="solar:arrow-up-linear"
                    width={20}
                  />
                )}
              </Button>
            </Tooltip>
          </div>
        }
        startContent={
          <Tooltip showArrow content="Attach file (txt, md, pdf, xlsx)">
            <Button
              isIconOnly
              className="p-[10px]"
              isDisabled={isLoading}
              radius="full"
              variant="light"
              type="button"
              onPress={() => fileInputRef.current?.click()}
            >
              <Icon className="text-default-500" icon="solar:paperclip-linear" width={20} />
            </Button>
          </Tooltip>
        }
      />
    </form>
  );
}
