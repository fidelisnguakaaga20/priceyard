import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/** Phone-only tab bar fixed to the bottom of the screen: the five main sections are
 * always one tap away. Other links (Help, About, Feedback, ...) are listed on the
 * Account page. Hidden on wider screens, where every link is in the top bar. */

function Icon({ children }: { children: ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width="22"
      height="22"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

const ICONS = {
  prices: (
    <Icon>
      <path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8Z" />
      <circle cx="7.5" cy="7.5" r="1.5" />
    </Icon>
  ),
  history: (
    <Icon>
      <path d="M3 3v18h18" />
      <path d="m7 15 4-4 3 3 5-6" />
    </Icon>
  ),
  marketDays: (
    <Icon>
      <rect x="3" y="5" width="18" height="16" rx="2" />
      <path d="M16 3v4M8 3v4M3 10h18" />
    </Icon>
  ),
  watchlist: (
    <Icon>
      <path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9L12 3Z" />
    </Icon>
  ),
  account: (
    <Icon>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c0-4 3.6-7 8-7s8 3 8 7" />
    </Icon>
  ),
  help: (
    <Icon>
      <circle cx="12" cy="12" r="9" />
      <path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6V14" />
      <path d="M12 17.5h.01" />
    </Icon>
  ),
  login: (
    <Icon>
      <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
      <path d="m10 17 5-5-5-5M15 12H3" />
    </Icon>
  ),
};

export function BottomTabs() {
  const { user } = useAuth();
  const tabs: [string, string, ReactNode][] = [
    ["/prices", "Prices", ICONS.prices],
    ["/history", "History", ICONS.history],
    ["/market-days", "Market Days", ICONS.marketDays],
    ...(user
      ? ([
          ["/watchlist", "Watchlist", ICONS.watchlist],
          ["/dashboard", "Account", ICONS.account],
        ] as [string, string, ReactNode][])
      : ([
          ["/faq", "Help", ICONS.help],
          ["/login", "Log in", ICONS.login],
        ] as [string, string, ReactNode][])),
  ];
  return (
    <nav className="bottom-tabs" aria-label="Main sections">
      {tabs.map(([to, label, icon]) => (
        <NavLink key={to} to={to} className="bottom-tab">
          {icon}
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
