import { useState } from "react";

const MeetingSetup = () => {
  const [meetingName, setMeetingName] = useState("");
  const [meetingDate, setMeetingDate] = useState("");
  const [organizer, setOrganizer] = useState("");
  const [invitees, setInvitees] = useState("");
  const [agenda, setAgenda] = useState("");

  const handleSave = () => {
    // 保存処理を実装
  };

  const handleCancel = () => {
    // キャンセル処理を実装
  };

  return (
    <div>
      <h1>会議の初期設定</h1>
      <input
        type="text"
        placeholder="会議名"
        value={meetingName}
        onChange={(e) => setMeetingName(e.target.value)}
      />
      <input
        type="datetime-local"
        value={meetingDate}
        onChange={(e) => setMeetingDate(e.target.value)}
      />
      <input
        type="text"
        placeholder="主催者の名前またはID"
        value={organizer}
        onChange={(e) => setOrganizer(e.target.value)}
      />
      <input
        type="text"
        placeholder="招待者リスト（カンマ区切り）"
        value={invitees}
        onChange={(e) => setInvitees(e.target.value)}
      />
      <textarea
        placeholder="アジェンダ"
        value={agenda}
        onChange={(e) => setAgenda(e.target.value)}
      />
      <button onClick={handleSave}>保存</button>
      <button onClick={handleCancel}>キャンセル</button>
    </div>
  );
};

export default MeetingSetup;
