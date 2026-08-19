# Reflection — Lab 19

**Tên:** Nguyễn Đình Bình
**Cohort:** _K3_
**Path đã chạy:** lite (Windows)

## Câu hỏi

Trên golden set, BM25 mạnh nhất ở nhóm `exact` (96.7%) vì thuật ngữ kỹ thuật xuất hiện nguyên văn. Semantic phù hợp với paraphrase về mặt ý tưởng, nhưng model BGE-small tiếng Anh trên dữ liệu tiếng Việt làm kết quả chưa ổn định. Hybrid thắng rõ ở nhóm `mixed` (100.0%) và thắng trung bình (78.6%, so với BM25 77.8% và semantic 73.2%) nhờ kết hợp lexical và semantic bằng RRF. Tôi không dùng hybrid khi query exact, corpus nhỏ hoặc cần tối ưu latency tuyệt đối; BM25 đơn giản và nhanh hơn. Với production tiếng Việt, tôi sẽ cân nhắc bge-m3 rồi re-index corpus.

## Điều bất ngờ nhất

Embedding model ảnh hưởng mạnh hơn việc tinh chỉnh RRF: hybrid tốt tổng thể, nhưng semantic riêng lẻ yếu trên paraphrase tiếng Việt.

## Bonus challenge

- [ ]  Đã làm bonus
- [ ]  Pair work với: _<tên đồng đội nếu có>_
