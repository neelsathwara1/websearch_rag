# Meta Campaign JSON Schema with Enums and Field Descriptions

---

## âœ¨ Campaign Object

```json
{
  "name": "string",
  "objective": "CAMPAIGN_OBJECTIVE",
  "status": "CONFIGURED_STATUS",
  "special_ad_categories": ["string"],
  "buying_type": "BUYING_TYPE",
  "spend_cap": "integer",
  "promoted_object": {
    "pixel_id": "string",
    "product_catalog_id": "string",
    "custom_event_type": "CUSTOM_EVENT"
  },
  "start_time": "ISO8601 datetime",
  "stop_time": "ISO8601 datetime or null",
  "is_skadnetwork_enabled": "boolean",
  "is_dynamic_ad": "boolean",
  "delivery_type": "DeliveryType",
  "budget_auto_target_cpa_micro": "integer or null"
}
```

### Field Descriptions & Enums

- **name**: Campaign name.
- **objective**: Objective of the campaign.
  - Enums: BRAND_AWARENESS, CONVERSIONS, LEAD_GENERATION, TRAFFIC, VIDEO_VIEWS, POST_ENGAGEMENT, REACH, PAGE_LIKES, APP_INSTALLS
- **status**: Initial status of the campaign.
  - Enums: ACTIVE, PAUSED, DELETED
- **special_ad_categories**: Regulatory categories.
  - Examples: HOUSING, EMPLOYMENT, CREDIT, NONE
- **buying_type**: Auction type.
  - Enums: AUCTION, FIXED_CPM, RESERVED
- **spend_cap**: Maximum spend limit.
- **promoted_object**: Target object details.
  - pixel_id, product_catalog_id: IDs for pixel or catalog.
  - custom_event_type: Action being optimized for.
    - Enums: PURCHASE, LEAD, COMPLETE_REGISTRATION, etc.
- **delivery_type**: Ad delivery mode.
  - Enums: STANDARD, ACCELERATED

---

## ðŸ“¢ Ad Set Object

```json
{
  "name": "string",
  "campaign_id": "string",
  "status": "CONFIGURED_STATUS",
  "daily_budget": "integer",
  "lifetime_budget": "integer",
  "billing_event": "BILLING_EVENT",
  "bid_strategy": "BID_STRATEGY",
  "bid_amount": "integer",
  "optimization_goal": "OPTIMIZATION_GOAL",
  "start_time": "ISO8601 datetime",
  "end_time": "ISO8601 datetime or null",
  "targeting": {
    "age_min": "integer",
    "age_max": "integer",
    "genders": ["integer"],
    "geo_locations": {
      "countries": ["string"],
      "cities": [{"key": "string", "radius": integer, "distance_unit": "mile"}]
    }
  }
}
```

### Field Descriptions & Enums

- **billing_event**: Action that triggers billing.
  - Enums: APP_INSTALLS, IMPRESSIONS, LINK_CLICKS, PURCHASE
- **bid_strategy**: Bidding method.
  - Enums: LOWEST_COST_WITHOUT_CAP, LOWEST_COST_WITH_BID_CAP, TARGET_COST
- **optimization_goal**: Optimization focus.
  - Enums: OFFSITE_CONVERSIONS, APP_INSTALLS, PAGE_LIKES, LINK_CLICKS, VIDEO_VIEWS
- **targeting**: Audience definition.
  - age_min / age_max: Range of target audience.
  - genders: 1 (Male), 2 (Female)
  - geo_locations: country and city-level targeting.

---

## ðŸ“° Ad Creative & Ad Object

```json
{
  "name": "string",
  "adset_id": "string",
  "status": "CONFIGURED_STATUS",
  "creative": {
    "object_story_spec": {
      "page_id": "string",
      "instagram_actor_id": "string",
      "link_data": {
        "message": "string",
        "link": "url",
        "child_attachments": [
          {
            "link": "url",
            "image_hash": "string",
            "name": "string"
          }
        ],
        "call_to_action": {
          "type": "CTA_TYPE",
          "value": {"link": "url"}
        }
      }
    }
  }
}
```

### Field Descriptions & Enums

- **status**: Ad state.
  - Enums: ACTIVE, PAUSED, DELETED
- **object_story_spec**: Content of the ad.
- **link_data**: Link metadata for the ad.
- **call_to_action.type**:
  - Enums: SHOP_NOW, LEARN_MORE, SIGN_UP, DOWNLOAD, WATCH_MORE
- **image_hash**: Hash of previously uploaded image.

---

This document provides a complete Meta Marketing API campaign schema including all relevant enums and definitions for scalable automation.

