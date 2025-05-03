from uuid import uuid4

from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema.message import Message
from langflow.services.deps import get_storage_service
from langflow.template.field.base import Input


class TextFileDownloadComponent(Component):
    display_name = "Save as Text File"
    description = "Save text output to a file and provide a download link."
    icon = "file-text-2"
    name = "TextFileDownload"

    inputs = [
        MessageTextInput(
            name="text",
            display_name="Text",
            info="Text content to save as a file.",
        ),
        Input(
            name="file_name",
            display_name="File Name",
            type="str",
            info="Name of the file (without extension).",
            default="output",
        ),
    ]
    outputs = [
        Output(display_name="Text File Link", name="file_link", method="save_text_file"),
    ]

    async def save_text_file(self) -> Message:
        """Save text content to a file and return a download link."""
        if not self.text:
            return Message(
                text="No text content to save.",
                error=True,
            )

        # Get text content
        text_content = self.text
        if isinstance(text_content, Message):
            text_content = text_content.text

        # Clean filename and add extension
        file_name = self.file_name.strip() if self.file_name else "output"
        file_name = file_name.replace(" ", "_")
        if not file_name.endswith(".txt"):
            file_name += ".txt"

        # Generate a unique flow ID if not in a graph context
        flow_id = str(self.flow_id) if hasattr(self, "flow_id") and self.flow_id else str(uuid4())

        try:
            # Get storage service and save file
            storage_service = get_storage_service()
            await storage_service.save_file(flow_id=flow_id, file_name=file_name, data=text_content.encode("utf-8"))

            # Create download link
            download_link = f"/api/v1/files/download/{flow_id}/{file_name}"

            # Create message with download link
            message = Message(
                text=f"File saved successfully. [Download Text File]({download_link})",
            )
            self.status = f"File saved as {file_name}"
        except (OSError, UnicodeError) as e:
            return Message(
                text=f"Error saving file: {e!s}",
                error=True,
            )
        else:
            return message
