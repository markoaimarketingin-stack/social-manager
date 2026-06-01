export type PlatformKey = "instagram" | "facebook" | "linkedin" | "x" | "youtube";

export type PlatformWorkspace = {
  key: PlatformKey;
  label: string;
  shortLabel: string;
  route: string;
  accent: string;
  description: string;
  publishingFocus: string;
  contentFormats: string[];
  operatingNotes: string[];
};

export const PLATFORM_WORKSPACES: PlatformWorkspace[] = [
  {
    key: "instagram",
    label: "Instagram",
    shortLabel: "IG",
    route: "platforms/instagram",
    accent: "#e1306c",
    description: "Visual-first publishing control for Reels, carousels, stories, and brand engagement.",
    publishingFocus: "Creative hooks, visual consistency, creator-style captions, and saved-content loops.",
    contentFormats: ["Reels", "Carousel posts", "Stories", "Static image captions"],
    operatingNotes: [
      "Requires an Instagram Business Account linked to a Facebook Page.",
      "Use the supervisor to adapt captions before dispatching through the publishing queue.",
      "Insights area is reserved for platform metrics once ingestion is enabled.",
    ],
  },
  {
    key: "facebook",
    label: "Facebook Page",
    shortLabel: "FB",
    route: "platforms/facebook",
    accent: "#1877f2",
    description: "Page publishing workspace for announcements, community updates, and evergreen campaigns.",
    publishingFocus: "Page updates, campaign posts, local/community engagement, and link distribution.",
    contentFormats: ["Page posts", "Link posts", "Community updates", "Campaign announcements"],
    operatingNotes: [
      "Uses the connected Facebook Page selected during OAuth or env-token import.",
      "Instagram publishing depends on Facebook Page permissions for Business accounts.",
      "Comment and inbox operations can attach here when community APIs are enabled.",
    ],
  },
  {
    key: "linkedin",
    label: "LinkedIn",
    shortLabel: "IN",
    route: "platforms/linkedin",
    accent: "#0077b5",
    description: "Professional distribution workspace for thought leadership and company updates.",
    publishingFocus: "Founder POV, B2B education, case-study snippets, and professional credibility.",
    contentFormats: ["Personal profile posts", "Company updates", "Document-style posts", "Thought leadership"],
    operatingNotes: [
      "OAuth supports personal identity today; organization posting can be layered when app access is approved.",
      "Use brand voice and audience segments to keep executive posts consistent.",
      "Draft queue shows LinkedIn-targeted jobs already created through publishing.",
    ],
  },
  {
    key: "x",
    label: "X / Twitter",
    shortLabel: "X",
    route: "platforms/x",
    accent: "#e6edf3",
    description: "Fast-cycle control surface for short-form posts, launch notes, and conversation hooks.",
    publishingFocus: "Concise announcements, threads, opinion hooks, and real-time market commentary.",
    contentFormats: ["Short posts", "Threads", "Launch notes", "Conversation prompts"],
    operatingNotes: [
      "Requires an X Developer app with OAuth 2.0 enabled.",
      "Thread composer and reply monitoring are placeholders until backend endpoints are added.",
      "Use trend intelligence to shape timely post angles before scheduling.",
    ],
  },
  {
    key: "youtube",
    label: "YouTube",
    shortLabel: "YT",
    route: "platforms/youtube",
    accent: "#ff0000",
    description: "Video channel workspace for Shorts, long-form planning, and campaign repurposing.",
    publishingFocus: "Shorts ideas, video descriptions, launch clips, and long-form topic planning.",
    contentFormats: ["Shorts", "Video descriptions", "Community posts", "Long-form outlines"],
    operatingNotes: [
      "OAuth support exists; upload/publishing capability depends on Google project scopes and verification.",
      "Use this page to track YouTube readiness alongside the rest of the publishing system.",
      "Analytics panels are prepared for channel/video metrics once ingestion endpoints exist.",
    ],
  },
];

export function getPlatformWorkspace(platformKey?: string): PlatformWorkspace | undefined {
  return PLATFORM_WORKSPACES.find((platform) => platform.key === platformKey);
}

