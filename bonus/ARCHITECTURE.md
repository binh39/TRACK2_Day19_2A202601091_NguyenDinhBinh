# Hybrid Memory Assistant — Architecture

## Mục tiêu

POC này kết hợp ba loại trí nhớ cho trợ lý tiếng Việt: episodic memory là các
cuộc hội thoại, tài liệu và ghi chú đã lưu; stable profile là thuộc tính chậm
thay đổi; recent activity là tín hiệu ngắn hạn như số truy vấn trong một giờ.
Vector store trả lời “thông tin nào liên quan?”, còn Feature Store trả lời
“người dùng này là ai và đang ở trạng thái nào?”. LLM, nếu được cấu hình, chỉ
nhận context đã được ground và không tự truy cập database.

## Sơ đồ kiến trúc

```text
conversation / note / document
          │ chunk + metadata (user_id, topic, timestamp)
          ▼
   Qdrant episodic memory ── hybrid retrieval (BM25 + vector + RRF)
          │ top-K memories
          │
user profile Parquet ── PIT/offline ── Feast ── online profile + activity
          │                                     │
          └───────────────┬─────────────────────┘
                          ▼
                 build_context(user, query)
                          │
                          ▼
              optional OpenAI answer generation
```

## Quyết định 1 — chunking episodic memory

Tôi chọn chunk theo message hoặc đoạn văn khoảng 150–300 tokens, giữ
`conversation_id`, `user_id`, timestamp và topic trong payload. Chunk theo
từng message làm retrieval chính xác hơn: câu hỏi về Kubernetes không kéo theo
toàn bộ cuộc hội thoại dài. Đổi lại, context có thể thiếu phần trước đó, nên
production cần lưu `conversation_id` để mở rộng lân cận khi một chunk được
chọn. Chunk theo toàn bộ conversation giữ ngữ cảnh tốt hơn nhưng vector nghĩa
bị pha loãng, tốn context window và khó cập nhật. Semantic chunking có thể
nâng chất lượng ở tài liệu dài, nhưng chi phí ingest và độ khó kiểm thử cao
hơn. Fixed-size paragraph là cân bằng hợp lý cho POC giữa chất lượng, storage
cost và tính tái lập.

## Quyết định 2 — feature schema

Profile gồm `preferred_language`, `reading_speed_wpm`, `topic_affinity` và
`active_hours`; mỗi feature có entity `user_id`, source, timestamp và TTL.
`topic_affinity` và ngôn ngữ có TTL khoảng 30 ngày; `queries_last_hour` và
`topic_spike` thuộc activity view có TTL 1 giờ. Tôi dùng tabular features cho
serving vì chúng dễ giải thích, PIT join được và lookup nhanh. Embedding
profile có thể biểu diễn sở thích phong phú hơn, nhưng khó debug, khó kiểm tra
privacy và không cần thiết cho quyết định đơn giản như chọn topic filter.
Vector episodic memory vẫn giữ phần giàu ngữ nghĩa.

## Quyết định 3 — freshness

Sau khi người dùng lưu ghi chú, episodic vector nên cập nhật trong vài giây
bằng push/upsert. `queries_last_hour` nên refresh gần real-time hoặc mỗi phút;
trễ 5 phút có thể làm trợ lý bỏ lỡ topic spike. Reading speed và topic affinity
có thể batch mỗi ngày, vì một lần đọc không nên làm profile dao động ngay.
Tôi chọn streaming cho recent activity, batch cho profile và asynchronous
upsert cho episodic memory: đây là trade-off giữa freshness, chi phí vận hành
và độ ổn định của feature.

## Alternative bị loại

Tôi đã cân nhắc lưu episodic memories như embedding feature view trong Feast,
nhưng chọn tách sang Qdrant vì hai vòng đời khác nhau: memory tăng theo từng
message và cần approximate nearest-neighbor search, trong khi profile có schema
ổn định, TTL rõ và cần PIT training join. Gộp chúng làm materialization phức
tạp, đồng thời khiến xóa/isolate memory theo user khó hơn.

## Vietnamese-context và bảo mật

Corpus có code-switching Việt–Anh, dấu tiếng Việt và từ kỹ thuật như Kubernetes,
OAuth, Kafka. Whitespace tokenization là baseline dễ chạy nhưng không xử lý
tốt từ ghép hoặc lỗi gõ; production nên benchmark `underthesea`, `pyvi` và
multilingual embedding như bge-m3. Payload luôn có `user_id` và mọi query phải
filter theo user/tenant trước khi dựng context. Semantic cache phải namespace
theo tenant; nếu bỏ namespace, câu trả lời của user A có thể leak sang user B.
API key chỉ nằm trong `.env`, không ghi vào payload, notebook output hay Git.

## Giới hạn hiện tại

POC chưa có encryption at rest, CRUD/forgetting policy, multi-device sync,
stream processor thật hoặc authorization service. OpenAI generation là lớp
tùy chọn; retrieval local vẫn chạy được khi không có mạng/API key.
