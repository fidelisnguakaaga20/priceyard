export type User = {
  id: number;
  full_name: string;
  email: string;
  phone: string | null;
  role: "admin" | "free_user" | "paid_user" | string;
  is_active: boolean;
  referred_by_id: number | null;
  created_at: string;
};

export type ActivityEvent = {
  id: number;
  event_type: "app_visit" | "share_view" | string;
  label: string | null;
  created_at: string;
};

export type ActivitySummary = {
  unseen_count: number;
  recent: ActivityEvent[];
};

export type SubscriptionStatus = "free" | "trial" | "active" | "expired" | "cancelled";

export type Subscription = {
  id: number;
  user_id: number;
  plan_name: string;
  status: SubscriptionStatus;
  trial_started_at: string | null;
  trial_ends_at: string | null;
  start_date: string | null;
  end_date: string | null;
  payment_reference: string | null;
  created_at: string;
  updated_at: string;
};

export type Commodity = {
  id: number;
  name: string;
  description: string | null;
  image_url: string | null;
  is_active: boolean;
  is_upcoming: boolean;
  expected_available_date: string | null;
  created_at: string;
  updated_at: string;
};

export type Market = {
  id: number;
  name: string;
  state: string | null;
  country: string;
  market_day: string | null;
  description: string | null;
  image_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type PriceUpdate = {
  id: number;
  commodity_id: number;
  market_id: number;
  commodity: { id: number; name: string; image_url: string | null };
  market: { id: number; name: string; state: string | null; market_day: string | null };
  price_low: string | number;
  price_high: string | number;
  average_price: string | number | null;
  previous_price_low: string | number | null;
  previous_price_high: string | number | null;
  unit: string;
  bag_size: string | null;
  commodity_type: string | null;
  market_day: string | null;
  time_of_day: string | null;
  movement: "up" | "down" | "stable" | "unknown" | string;
  confidence_level: string;
  source_type: string | null;
  update_date_time: string;
  is_outdated: boolean;
  status: string;
  possible_meaning: string | null;
  suggested_action: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type MarketSignal = {
  id: number;
  commodity_id: number;
  market_id: number;
  price_update_id: number | null;
  signal_type: string;
  signal_description: string;
  possible_meaning: string | null;
  suggested_action: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  disclaimer?: string;
};

export type QualitySignal = {
  id: number;
  commodity_id: number;
  market_id: number;
  price_update_id: number | null;
  quality_status: string | null;
  moisture_status: string | null;
  storage_readiness: string | null;
  risk_note: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
};

export type BuyingZone = {
  id: number;
  commodity_id: number;
  market_id: number;
  price_low: string | number;
  price_high: string | number;
  reason: string;
  valid_from: string | null;
  valid_to: string | null;
  confidence: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  disclaimer: string;
};

export type SellWatchWindow = {
  id: number;
  commodity_id: number;
  market_id: number;
  start_period: string;
  end_period: string | null;
  observation: string;
  confidence: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  disclaimer: string;
};

export type StorageSuitability = {
  id: number;
  commodity_id: number;
  market_id: number;
  price_update_id: number | null;
  suitability_status: "good" | "watch" | "risky" | "not_recommended";
  import_risk: string | null;
  oversupply_risk: string | null;
  spoilage_risk: string | null;
  buyer_availability: string | null;
  quality_storage_notes: string | null;
  summary: string | null;
  created_at: string;
  updated_at: string;
  disclaimer: string;
};

export type CostBreakdown = {
  id: number;
  commodity_id: number;
  market_id: number;
  transport: string | number;
  warehouse: string | number;
  security: string | number;
  market_charges: string | number;
  loading_offloading: string | number;
  other_costs: string | number;
  total_additional_cost: string | number;
  purchase_price_reference: string | number;
  total_estimated_landing_storage_cost: string | number;
  created_at: string;
  updated_at: string;
};

export type FAQItem = {
  id: number;
  question: string;
  answer: string;
  category: string;
  created_at: string;
  updated_at: string;
};

export type TargetDirection = "at_or_below" | "at_or_above";

export type WatchlistItem = {
  id: number;
  user_id: number;
  commodity_id: number | null;
  market_id: number | null;
  target_price: string | number | null;
  target_direction: TargetDirection | null;
  created_at: string;
  updated_at: string;
};

export type PriceUpdateAdmin = PriceUpdate & {
  source_1: string | null;
  source_2: string | null;
  created_by: number;
  approved_by: number | null;
};

export type FeedbackItem = {
  id: number; user_id: number; rating: number; comment: string | null; price_usefulness: string | null; price_accuracy: string | null;
  missing_market_request: string | null; missing_commodity_request: string | null; complaint_or_suggestion: string | null;
  continue_using_feedback: boolean | null; willingness_to_pay_feedback: boolean | null; created_at: string; updated_at: string;
};

export type FeedbackSummary = { count: number; average_rating: number | null };
export type Testimonial = { id: number; rating: number; quote: string; display_name: string; created_at: string };
export type ReferralSummary = { referral_code: string; referred_count: number; reward_days: number };
export type PaymentPlan = "monthly" | "seasonal";
export type PaymentInitiateResponse = { authorization_url: string; reference: string };
export type AuditLog = { id: number; user_id: number; action: string; table_name: string; record_id: number | null; old_value: unknown; new_value: unknown; created_at: string };
