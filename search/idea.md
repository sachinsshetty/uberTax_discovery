Search with Context

Under the hood, Nia is an indexing and retrieval service with an MCP interface and an API. You
point it at sources like GitHub repositories, framework or provider docs, SDK pages, PDF
manuals, etc. We fetch and parse those with some simple heuristics for code structures,
headings, and tables, then normalize them into chunks and build several indexes: a semantic
index with embeddings for natural language queries; a symbol and usage index for functions,
classes, types, and endpoints; a basic reference graph between files, symbols, and external
docs; regex and file tree search for cases where you want deterministic matches over raw text.
When an agent calls Nia, it sends a natural language query plus optional hints like the current
file path, stack trace, or repository. Nia runs a mix of BM25 style search, embedding similarity,
and graph walks to rank relevant snippets, and can also return precise locations like “this
function definition in this file and the three places it is used” instead of just a fuzzy paragraph.
The calling agent then decides how to use those snippets in its own prompt. One Nia
deployment can serve multiple agents and multiple projects at once. For example, you can have
Cursor, Claude Code, and a browser based agent all pointed at the same Nia instance that
knows about your monorepo, your internal wiki, and the provider docs you care about. We keep
an agent agnostic session record that tracks which sources were used and which snippets the
user accepted. Any MCP client can attach to that session id, fetch the current context, and
extend it, so switching tools does not mean losing what has already been discovered.