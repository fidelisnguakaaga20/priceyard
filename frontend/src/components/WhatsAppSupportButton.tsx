const SUPPORT_WHATSAPP_NUMBER = "2347031128081";

export function WhatsAppSupportButton() {
  const text = encodeURIComponent("Hi PriceYard, I need help with...");
  return (
    <a
      className="whatsapp-support-button"
      href={`https://wa.me/${SUPPORT_WHATSAPP_NUMBER}?text=${text}`}
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Chat with PriceYard support on WhatsApp"
      title="Chat with us on WhatsApp"
    >
      <svg viewBox="0 0 32 32" width="28" height="28" fill="currentColor" aria-hidden="true">
        <path d="M16.004 3C9.377 3 4 8.373 4 15c0 2.34.68 4.522 1.86 6.36L4 29l7.83-1.83A11.93 11.93 0 0 0 16.004 27C22.63 27 28 21.627 28 15S22.63 3 16.004 3Zm0 21.6a9.55 9.55 0 0 1-4.87-1.34l-.35-.21-4.65 1.09 1.11-4.53-.23-.37A9.56 9.56 0 1 1 25.56 15a9.57 9.57 0 0 1-9.56 9.6Zm5.24-7.17c-.29-.15-1.7-.84-1.96-.94-.26-.1-.46-.15-.65.15-.19.29-.75.94-.92 1.13-.17.19-.34.22-.63.07-.29-.15-1.22-.45-2.32-1.43-.86-.77-1.44-1.71-1.61-2-.17-.29-.02-.45.13-.6.13-.13.29-.34.44-.51.15-.17.19-.29.29-.48.1-.19.05-.36-.02-.51-.07-.15-.65-1.56-.89-2.14-.23-.56-.47-.48-.65-.49h-.55c-.19 0-.51.07-.78.36-.26.29-1.02 1-1.02 2.43s1.05 2.82 1.19 3.01c.15.19 2.07 3.16 5.02 4.43.7.3 1.25.48 1.68.61.7.22 1.34.19 1.85.12.56-.08 1.7-.7 1.94-1.37.24-.68.24-1.26.17-1.38-.07-.12-.26-.19-.55-.34Z" />
      </svg>
    </a>
  );
}
