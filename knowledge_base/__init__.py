# finsage/knowledge_base/__init__.py
# Knowledge-base sub-package.
# Exposes the DOCUMENTS list so any module can import cleanly:
#
#   from knowledge_base import DOCUMENTS
#
from knowledge_base.documents import DOCUMENTS

__all__ = ["DOCUMENTS"]
