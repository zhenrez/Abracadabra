# Original bytes for the newest account uploads

Current acquisition scope: the newest80–100 images uploaded across the account, without reuploading and without a Favorites-only or filename filter. This subtask inspected tool contracts and official documentation; it did not operate a browser or retrieve any account image.

Actual SuperJev selected `library_original_download` with model mass0.61 versus `authorized_widget_file_bridge`0.39, resolved model `jev-1.14.0`. The complete request/result are `docs/evidence/account-image-retrieval-request.json` and `account-image-retrieval-result.json`. This ranks the supplied execution alternatives; it establishes no file availability or permission.

## Concrete acquisition route

The root agent's existing authenticated browser can open the actual Library, or Space where it replaces Library, observe the Uploaded and Images filters, verify the displayed newest ordering, and download selected existing files. The official Library guide documents those filters and selection/download behavior. Favorites is a separate saved-item view; an empty Favorites view does not enumerate all uploaded images. [OpenAI Library guide](https://help.openai.com/en/articles/20001052-using-library-to-manage-files-in-chatgpt).

Preserve each observed file ID, source conversation where supplied, upload-date precision, observed ordering, original filename, original byte count, MIME signature, dimensions and SHA256. An exported reference is an acquisition lead; original bytes establish the image evidence. Generated-image galleries, thumbnails and stale signed URLs do not establish which originals were recovered. The UI's actual ordering must be observed; documentation alone does not certify a newest100 census.

## Native image-reader tools actually available

`mcp__codex_apps__chatgpt_space_inspect_page_reference` accepts:

```ts
{ page_id: string, reference: string }
```

Both values must be observed: an accessible Page ID and its exact opaque `project-file:`, `library-file:` or `visualize:` reference. Inspection returns authorized metadata where available; missing metadata is not a finding that the file is missing.

`mcp__codex_apps__chatgpt_space_read_page_reference` accepts the same shape. For authorized PNG/JPEG/GIF/WebP files up to10MiB, it returns MCP image content and original-file `byte_size`, `mime_type` and `sha256`. It detects the raster format from bytes. SVG returns source text. For supported document formats it returns bounded extracted text; that is not a substitute for original raster images.

A historical attachment ID such as an observed `file_...` is not the required Page reference. Do not manufacture `library-file:` syntax from it. The Pages listing was already exhausted at0Spaces/3Pages; repeating it does not create missing file references, and that listing is not an account-wide upload census.

## Documented host file bridge

In an actual ChatGPT plugin runtime, feature-detect the optional `window.openai.selectFiles()` and `window.openai.getFileDownloadUrl({fileId})` methods. The first selects existing Library files and returns `{fileId,fileName,mimeType}` objects. The second obtains a temporary download URL for files authorized to that plugin through selection, file inputs, widget upload or tool file references. This is an existing-file route, not a request to upload the images again. [Official Plugins file APIs](https://developers.openai.com/plugins/reference#file-apis).

A tool file input authorized by the host has this documented shape:

```ts
{
  download_url: string,
  file_id: string,
  mime_type?: string,
  file_name?: string
}
```

That is a host-provided file object. The model must not invent its URL or assume that a bare historical file ID grants current-plugin access. No enabled standalone tool equivalent to account-wide `list_chatgpt_uploads` or arbitrary `download_chatgpt_file(file_id)` was found in the inspected tool catalog. The widget bridge is useful only if an actual authorized plugin runtime exposes it; it was not executed by this subtask.

## Capabilities that do not fill this gap

- `mcp__codex_apps__codex_document_control_list_document_sessions` concerns connected Excel, PowerPoint, Word or Sheets sessions. Its supplied surface schema does not enumerate ChatGPT account uploads.
- `mcp__codex_apps__sentinelx_sentinel_file_upload_attachment` requires a current attachment/local file path and a destination on a connected host. It is not a historical ChatGPT file-ID lookup.
- Provider-specific media libraries enumerate that provider's assets, not ChatGPT's uploads. Importing images into another provider is a different operation and is unnecessary for this original-byte retrieval.
- Local `view_image` can inspect a genuinely downloaded original after acquisition. It does not fetch remote account images by file ID.

The account-wide route, native Page-reference route and widget file-bridge route remain distinct. Use actual returned identities, verify the bytes, and attach extraction results under `FAVORITES_REVIEW_PROTOCOL.md`, whose scope note now preserves the broader80–100-upload correction. No source grammar or orientation finding follows from the capability investigation itself.
