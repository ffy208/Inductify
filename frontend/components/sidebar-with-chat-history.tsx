"use client";

import type {ComponentProps} from "react";

import React from "react";
import {
  Avatar,
  Button,
  ScrollShadow,
  Spacer,
  useDisclosure,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  DropdownSection,
  cn,
} from "@heroui/react";
import {Icon} from "@iconify/react";

import type {Conversation} from "./app";

import {InductifyIcon} from "./acme";
import SidebarDrawer from "./sidebar-drawer";

/**
 * 💡 TIP: You can use the usePathname hook from Next.js App Router to get the current pathname
 * and use it as the active key for the Sidebar component.
 *
 * ```tsx
 * import {usePathname} from "next/navigation";
 *
 * const pathname = usePathname();
 * const currentPath = pathname.split("/")?.[1]
 *
 * <Sidebar defaultSelectedKey="home" selectedKeys={[currentPath]} />
 * ```
 */

function AvatarDropdownIcon(props: ComponentProps<"svg">) {
  return (
    <svg
      {...props}
      fill="none"
      height="20"
      viewBox="0 0 20 20"
      width="20"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g clipPath="url(#clip0_3076_10614)">
        <path
          d="M6.6665 7.50008L9.99984 4.16675L13.3332 7.50008"
          stroke="#A1A1AA"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M13.3332 12.5L9.99984 15.8333L6.6665 12.5"
          stroke="#A1A1AA"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </g>
      <defs>
        <clipPath id="clip0_3076_10614">
          <rect fill="white" height="20" width="20" />
        </clipPath>
      </defs>
    </svg>
  );
}

function RecentPromptDropdown() {
  return (
    <Dropdown>
      <DropdownTrigger>
        <Icon
          className="text-default-500 opacity-0 group-hover:opacity-100"
          icon="solar:menu-dots-bold"
          width={24}
        />
      </DropdownTrigger>
      <DropdownMenu aria-label="Dropdown menu with icons" className="py-2" variant="faded">
        <DropdownItem
          key="share"
          className="text-default-500 data-[hover=true]:text-default-500"
          startContent={
            <Icon
              className="text-default-300"
              height={20}
              icon="solar:square-share-line-linear"
              width={20}
            />
          }
        >
          Share
        </DropdownItem>
        <DropdownItem
          key="rename"
          className="text-default-500 data-[hover=true]:text-default-500"
          startContent={
            <Icon className="text-default-300" height={20} icon="solar:pen-linear" width={20} />
          }
        >
          Rename
        </DropdownItem>
        <DropdownItem
          key="archive"
          className="text-default-500 data-[hover=true]:text-default-500"
          startContent={
            <Icon
              className="text-default-300"
              height={20}
              icon="solar:folder-open-linear"
              width={20}
            />
          }
        >
          Archive
        </DropdownItem>
        <DropdownItem
          key="delete"
          className="text-danger-500 data-[hover=true]:text-danger-500"
          color="danger"
          startContent={
            <Icon
              className="text-danger-500"
              height={20}
              icon="solar:trash-bin-minimalistic-linear"
              width={20}
            />
          }
        >
          Delete
        </DropdownItem>
      </DropdownMenu>
    </Dropdown>
  );
}

export default function Component({
  children,
  header,
  title,
  subTitle,
  classNames = {},
  conversations = [],
  activeConversationId = null,
  onSelectConversation,
  onNewChat,
}: {
  children?: React.ReactNode;
  header?: React.ReactNode;
  title?: string;
  subTitle?: string;
  classNames?: Record<string, string>;
  conversations?: Conversation[];
  activeConversationId?: string | null;
  onSelectConversation?: (id: string) => void;
  onNewChat?: () => void;
}) {
  const {isOpen, onOpen, onOpenChange} = useDisclosure();

  const content = (
    <div className="relative flex h-full w-72 flex-1 flex-col p-6">
      <div className="flex items-center gap-2 px-2">
        <img src="/LOGO2.png" alt="Inductify" className="h-8 w-8 rounded-full object-cover" />
        <span className="text-base font-bold uppercase leading-6 text-foreground">Inductify AI</span>
      </div>

      <Spacer y={8} />

      <div className="flex flex-col gap-4">
        <Dropdown placement="bottom-end">
          <DropdownTrigger>
            <Button
              fullWidth
              className="h-[60px] justify-start gap-3 rounded-[14px] border-1 border-default-300 bg-transparent px-3 py-[10px]"
              endContent={<AvatarDropdownIcon height={20} width={20} />}
            >
              <div className="flex w-full items-center gap-3">
                <Avatar
                  size="sm"
                  src="/YahaUsagi.webp"
                />
                <div className="flex flex-col text-left">
                  <p className="text-small font-semibold leading-5 text-foreground">Usagi</p>
                  <p className="text-tiny text-default-400">usagi@inductify.ai</p>
                </div>
              </div>
            </Button>
          </DropdownTrigger>
          <DropdownMenu
            aria-label="Profile Actions"
            className="w-[210px] bg-content1 px-[8px] py-[8px]"
            variant="flat"
          >
            <DropdownItem key="profile" className="h-14">
              <div className="flex w-full items-center gap-3">
                <Avatar
                  size="sm"
                  src="/YahaUsagi.webp"
                />
                <div className="flex flex-col text-left">
                  <p className="text-small font-normal leading-5 text-foreground">Usagi</p>
                  <p className="text-tiny text-default-400">usagi@inductify.ai</p>
                </div>
              </div>
            </DropdownItem>
            <DropdownSection showDivider aria-label="profile-section-1" className="px-0">
              <DropdownItem key="my-plan" className="py-[4px] text-default-500">
                My Plan
              </DropdownItem>
              <DropdownItem key="my-gpts" className="py-[4px] text-default-500">
                My GPTs
              </DropdownItem>
              <DropdownItem key="customize-acmeai" className="py-[4px] text-default-500">
                Customize Inductify
              </DropdownItem>
            </DropdownSection>
            <DropdownSection showDivider aria-label="profile-section-2">
              <DropdownItem key="settings" className="py-[4px] text-default-500">
                Settings
              </DropdownItem>
              <DropdownItem key="download-desktop-app" className="py-[4px] text-default-500">
                Download Desktop App
              </DropdownItem>
            </DropdownSection>
            <DropdownSection aria-label="profile-section-3" className="mb-0">
              <DropdownItem key="help-and-feedback" className="py-[4px] text-default-500">
                Help & Feedback
              </DropdownItem>
              <DropdownItem key="logout" className="pt-[4px] text-default-500">
                Log Out
              </DropdownItem>
            </DropdownSection>
          </DropdownMenu>
        </Dropdown>
      </div>

      <ScrollShadow className="-mr-6 h-full max-h-full pr-6">
        <Button
          fullWidth
          className="mb-6 mt-2 h-[44px] justify-start gap-3 bg-default-foreground px-3 py-[10px] text-default-50"
          startContent={
            <Icon className="text-default-50" icon="solar:chat-round-dots-linear" width={24} />
          }
          onPress={onNewChat}
        >
          New Chat
        </Button>

        {conversations.length > 0 && (
          <div className="flex flex-col">
            <p className="pb-1 pl-[10px] text-small text-default-400">Recent</p>
            {conversations.map((conv) => (
              <button
                key={conv.id}
                className={cn(
                  "group flex h-[44px] w-full items-center justify-between rounded-medium px-[12px] py-[10px] text-left text-small text-default-500 transition-colors hover:bg-default-100",
                  activeConversationId === conv.id && "bg-default-200 text-foreground",
                )}
                type="button"
                onClick={() => onSelectConversation?.(conv.id)}
              >
                <span className="truncate">{conv.title}</span>
                {/* stop click bubbling so the 3-dot menu doesn't also load the conversation */}
                <span onClick={(e) => e.stopPropagation()}>
                  <RecentPromptDropdown />
                </span>
              </button>
            ))}
          </div>
        )}
      </ScrollShadow>

      <Spacer y={8} />

      <div className="mt-auto flex flex-col">
        <Button
          fullWidth
          className="justify-start text-default-600"
          startContent={
            <Icon className="text-default-600" icon="solar:info-circle-line-duotone" width={24} />
          }
          variant="light"
        >
          Help
        </Button>
        <Button
          className="justify-start text-default-600"
          startContent={
            <Icon className="text-default-600" icon="solar:history-line-duotone" width={24} />
          }
          variant="light"
        >
          Activity
        </Button>

        <Button
          className="justify-start text-default-600"
          startContent={
            <Icon
              className="text-default-600"
              icon="solar:settings-minimalistic-line-duotone"
              width={24}
            />
          }
          variant="light"
        >
          Settings
        </Button>
      </div>
    </div>
  );

  return (
    <div className="flex h-full min-h-[48rem] w-full py-4">
      <SidebarDrawer
        className="h-full flex-none rounded-[14px] bg-default-50"
        isOpen={isOpen}
        onOpenChange={onOpenChange}
      >
        {content}
      </SidebarDrawer>
      <div className="flex w-full flex-col px-4 sm:max-w-[calc(100%_-_288px)]">
        <header
          className={cn(
            "flex h-16 min-h-16 items-center justify-between gap-2 rounded-none rounded-t-medium border-small border-divider px-4 py-3",
            classNames?.["header"],
          )}
        >
          <Button isIconOnly className="flex sm:hidden" size="sm" variant="light" onPress={onOpen}>
            <Icon
              className="text-default-500"
              height={24}
              icon="solar:hamburger-menu-outline"
              width={24}
            />
          </Button>
          {(title || subTitle) && (
            <div className="w-full min-w-[120px] sm:w-auto">
              <div className="truncate text-small font-semibold leading-5 text-foreground">
                {title}
              </div>
              <div className="truncate text-small font-normal leading-5 text-default-500">
                {subTitle}
              </div>
            </div>
          )}
          {header}
        </header>
        <main className="flex h-full">
          <div className="flex h-full w-full flex-col gap-4 rounded-none rounded-b-medium border-0 border-b border-l border-r border-divider py-3">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
