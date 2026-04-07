"""Workout library tools for Intervals.icu MCP server."""

from typing import Annotated, Any

from fastmcp import Context

from ..auth import ICUConfig
from ..client import ICUAPIError, ICUClient  # noqa: F401
from ..response_builder import ResponseBuilder


async def get_workout_library(
    ctx: Context | None = None,
) -> str:
    """Get workout library folders and training plans.

    Returns all workout folders and training plans available to you, including
    your personal workouts, shared workouts, and any training plans you follow.

    Each folder contains structured workouts that can be applied to your calendar.

    Returns:
        JSON string with workout folders/plans
    """
    assert ctx is not None
    config: ICUConfig = ctx.get_state("config")

    try:
        async with ICUClient(config) as client:
            folders = await client.get_workout_folders()

            if not folders:
                return ResponseBuilder.build_response(
                    data={"folders": [], "count": 0},
                    metadata={
                        "message": "No workout folders found. Create folders in Intervals.icu to organize your workouts."
                    },
                )

            folders_data: list[dict[str, Any]] = []
            for folder in folders:
                folder_item: dict[str, Any] = {
                    "id": folder.id,
                    "name": folder.name,
                }

                if folder.description:
                    folder_item["description"] = folder.description
                if folder.num_workouts:
                    folder_item["num_workouts"] = folder.num_workouts

                # Training plan info
                if folder.start_date_local:
                    folder_item["start_date"] = folder.start_date_local
                if folder.duration_weeks:
                    folder_item["duration_weeks"] = folder.duration_weeks
                if folder.hours_per_week_min or folder.hours_per_week_max:
                    folder_item["hours_per_week"] = {
                        "min": folder.hours_per_week_min,
                        "max": folder.hours_per_week_max,
                    }

                folders_data.append(folder_item)

            # Categorize folders
            training_plans = [f for f in folders if f.duration_weeks is not None]
            regular_folders = [f for f in folders if f.duration_weeks is None]

            summary = {
                "total_folders": len(folders),
                "training_plans": len(training_plans),
                "regular_folders": len(regular_folders),
                "total_workouts": sum(f.num_workouts or 0 for f in folders),
            }

            result_data = {
                "folders": folders_data,
                "summary": summary,
            }

            return ResponseBuilder.build_response(
                data=result_data,
                query_type="workout_library",
            )

    except ICUAPIError as e:
        return ResponseBuilder.build_error_response(e.message, error_type="api_error")
    except Exception as e:
        return ResponseBuilder.build_error_response(
            f"Unexpected error: {str(e)}", error_type="internal_error"
        )


async def get_workouts_in_folder(
    folder_id: Annotated[int, "Folder ID to get workouts from"],
    ctx: Context | None = None,
) -> str:
    """Get all workouts in a specific folder or training plan.

    Returns detailed information about all workouts stored in a folder,
    including their structure, intensity, and training load.

    Args:
        folder_id: ID of the folder to browse

    Returns:
        JSON string with workout details
    """
    assert ctx is not None
    _ = ctx  # config not needed - this endpoint is not supported

    return ResponseBuilder.build_error_response(
        "The Intervals.icu API does not support listing individual workouts within a folder "
        "via the GET endpoint. Use get_workout_library to see folder details including "
        "workout counts, or access workouts through the Intervals.icu web interface.",
        error_type="not_supported",
    )
