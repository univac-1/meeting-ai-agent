import React from "react";

interface Meeting {
  name: string;
  url: string;
  date: string;
}

const MeetingURLConfirmation: React.FC<{ meeting: Meeting }> = ({
  meeting,
}) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(meeting.url);
    alert("URLがクリップボードにコピーされました");
  };

  const handleShare = () => {
    // 共有処理を実装
  };

  return (
    <div>
      <h1>会議URLの確認</h1>
      <p>会議名: {meeting.name}</p>
      <p>会議URL: {meeting.url}</p>
      <p>会議の日時: {meeting.date}</p>
      <button onClick={handleCopy}>コピー</button>
      <button onClick={handleShare}>共有</button>
    </div>
  );
};

export default MeetingURLConfirmation;
