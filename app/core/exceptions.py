from fastapi import HTTPException, status


class DocumentNotFoundError(HTTPException):
    def __init__(self, doc_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{doc_id}' not found.",
        )


class UnsupportedFileTypeError(HTTPException):
    def __init__(self, filename: str):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type not supported: '{filename}'. Supported: PDF, TXT, DOCX, MD.",
        )


class EmbeddingError(HTTPException):
    def __init__(self, detail: str = "Failed to generate embeddings."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class LLMError(HTTPException):
    def __init__(self, detail: str = "LLM request failed."):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        )
