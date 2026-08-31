from typing import Dict, Any


class LeadDiscoveryWorkflow:
    """Durable workflow for discovering, enriching, scoring leads."""

    async def run(self, ctx: Any, args: Dict[str, Any]):
        org_id = args["organization_id"]
        filters = args.get("filters", {})

        discovered = await ctx.execute_activity(
            "discover_leads",
            arg={"organization_id": org_id, "filters": filters},
        )

        processed = []
        for lead in discovered.get("leads", []):
            enriched = await ctx.execute_activity(
                "enrich_lead",
                arg={"lead_id": lead["lead_id"]},
            )
            verified = await ctx.execute_activity(
                "verify_lead",
                arg={"lead_id": lead["lead_id"]},
            )
            scored = await ctx.execute_activity(
                "score_lead",
                arg={"lead_id": lead["lead_id"]},
            )
            processed.append({
                "lead_id": lead["lead_id"],
                "score": scored.get("score", 0),
            })

        return {"processed_leads": processed}


class OutreachWorkflow:
    """Durable workflow for the 30-day outreach lifecycle with human handoff."""

    async def run(self, ctx: Any, args: Dict[str, Any]):
        lead_id = args["lead_id"]
        proposal = args.get("proposal")

        await ctx.execute_activity(
            "send_initial_outreach",
            arg={"lead_id": lead_id, "proposal": proposal},
        )

        for touch in range(1, 6):
            await ctx.execute_activity(
                "wait_for_response",
                arg={"lead_id": lead_id, "duration_days": 1},
            )
            replied = await ctx.execute_activity(
                "check_for_reply",
                arg={"lead_id": lead_id},
            )
            if replied.get("has_reply", False):
                await ctx.execute_activity(
                    "trigger_human_handoff",
                    arg={"lead_id": lead_id},
                )
                return {"handoff_triggered": True}

            if touch < 6:
                await ctx.execute_activity(
                    "send_followup",
                    arg={"lead_id": lead_id, "touch": touch},
                )

        return {"lifecycle_completed": True, "handoff": False}
