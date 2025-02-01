import axios from "axios";
import { Input, message, DatePicker, TimePicker, Button } from "antd"
import { useState } from "react"
import { version } from "../../../package.json"
import { useNavigate } from "react-router-dom"
import { CLOUD_RUN_ENDPOINT } from "@/config";
import dayjs from "dayjs";
import { CloseOutlined } from "@ant-design/icons";

import styles from "./index.module.scss"
import logoSrc from "@/assets/login_logo.png"

const { TextArea } = Input

const MeetingSchedulePage = () => {
  const nav = useNavigate()
  const [messageApi, contextHolder] = message.useMessage()
  const [meetingName, setMeetingName] = useState("")
  const [meetingPurpose, setMeetingPurpose] = useState("")
  const [startDate, setStartDate] = useState(dayjs())
  const [startTime, setStartTime] = useState(dayjs())
  const [endTime, setEndTime] = useState(dayjs())
  const [participants, setParticipants] = useState<string[]>([])
  const [participantInput, setParticipantInput] = useState("")
  const [agendaItems, setAgendaItems] = useState<{ topic: string; duration: string }[]>([])
  const [agendaInput, setAgendaInput] = useState("")
  const [durationInput, setDurationInput] = useState("")

  const onParticipantInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setParticipantInput(e.target.value)
  }

  const onParticipantInputKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && participantInput.trim()) {
      setParticipants([...participants, participantInput.trim()])
      setParticipantInput("")
    }
  }

  const removeParticipant = (index: number) => {
    setParticipants(participants.filter((_, i) => i !== index))
  }

  const onAgendaInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAgendaInput(e.target.value)
  }

  const onDurationInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDurationInput(e.target.value)
  }

  const onAgendaInputKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && agendaInput.trim() && durationInput.trim()) {
      setAgendaItems([...agendaItems, { topic: agendaInput.trim(), duration: durationInput.trim() }])
      setAgendaInput("")
      setDurationInput("")
    }
  }

  const removeAgendaItem = (index: number) => {
    setAgendaItems(agendaItems.filter((_, i) => i !== index))
  }

  const handleApiCall = async () => {
    try {
      const response = await axios.post(`${CLOUD_RUN_ENDPOINT}/meeting`, {
        meeting_name: meetingName,
        meeting_purpose: meetingPurpose,
        start_date: startDate.format("YYYY-MM-DD"),
        start_time: startTime.format("HH:mm"),
        end_time: endTime.format("HH:mm"),
        participants,
        agenda: agendaItems.map(item => ({ topic: item.topic, duration: item.duration })),
      });
      
      const meetingId = response.data?.data?.meeting_id;
      if (meetingId) {
        messageApi.success("Meeting scheduled successfully!");
        nav(`/meeting/${meetingId}`);
      } else {
        throw new Error("Meeting ID is undefined");
      }
    } catch (error) {
      console.error("Error calling API:", error);
      messageApi.error("Failed to schedule meeting.");
    }
  }

  const onClickJoin = () => {
    handleApiCall()
  }

  const onClickCancel = () => {
    nav("/")
  }

  return (
    <div className={styles.meetingSchedulePage}>
      {contextHolder}
      <section className={styles.content}>
        <div className={styles.title}>
          <div className={styles.logo}>
            <img src={logoSrc} alt="" />
          </div>
          <div className={styles.text}>Schedule Meeting</div>
        </div>
        <div className={styles.item}>
          <label>会議名</label>
          <Input
            allowClear
            placeholder="会議名を入力してください"
            onChange={(e) => setMeetingName(e.target.value)}
            value={meetingName}
          />
        </div>
        <div className={styles.item}>
          <label>会議の目的</label>
          <TextArea
            allowClear
            placeholder="会議の目的を入力してください"
            onChange={(e) => setMeetingPurpose(e.target.value)}
            value={meetingPurpose}
            rows={4}
          />
        </div>
        <div className={styles.item}>
          <label>開始日</label>
          <DatePicker
            style={{ width: "100%" }}
            placeholder="開始日を選択してください"
            onChange={(date) => setStartDate(date)}
            value={startDate}
          />
        </div>
        <div className={styles.item}>
          <label>開始時刻</label>
          <TimePicker
            style={{ width: "100%" }}
            format="HH:mm"
            placeholder="開始時刻を選択してください"
            onChange={(time) => setStartTime(time)}
            value={startTime}
          />
        </div>
        <div className={styles.item}>
          <label>終了時刻</label>
          <TimePicker
            style={{ width: "100%" }}
            format="HH:mm"
            placeholder="終了時刻を選択してください"
            onChange={(time) => setEndTime(time)}
            value={endTime}
          />
        </div>
        <div className={styles.item}>
          <label>参加者</label>
          <Input
            allowClear
            placeholder="参加者を入力してEnterを押してください"
            onChange={onParticipantInputChange}
            onKeyPress={onParticipantInputKeyPress}
            value={participantInput}
          />
        </div>
        <div className={styles.item}>
          {participants.map((participant, index) => (
            <div key={index} style={{ display: "flex", alignItems: "center" }}>
              <span style={{ flexGrow: 1 }}>{participant}</span>
              <Button type="link" icon={<CloseOutlined />} onClick={() => removeParticipant(index)} />
            </div>
          ))}
        </div>
        <div className={styles.item}>
          <label>アジェンダ</label>
          <Input
            allowClear
            placeholder="アジェンダと所要時間を入力してEnterを押してください"
            onChange={onAgendaInputChange}
            onKeyPress={onAgendaInputKeyPress}
            value={agendaInput}
          />
        </div>
        <div className={styles.item}>
          <label>アジェンダの所要時間(分)</label>
          <Input
            allowClear
            type="number"
            placeholder="アジェンダと所要時間を入力してEnterを押してください"
            onChange={onDurationInputChange}
            onKeyPress={onAgendaInputKeyPress}
            value={durationInput}
          />
        </div>
        <div className={styles.agendaList}>
          {agendaItems.map((item, index) => (
            <div key={index} style={{ display: "flex", alignItems: "center" }}>
              <span style={{ flexGrow: 1 }}>{item.topic} - {item.duration}分</span>
              <Button type="link" icon={<CloseOutlined />} onClick={() => removeAgendaItem(index)} />
            </div>
          ))}
        </div>
        <div className={styles.btn} onClick={onClickJoin}>
          Save
        </div>
        <div className={styles.cancelBtn} onClick={onClickCancel}>
          Cancel
        </div>
      </section>
    </div>
  )
}

export default MeetingSchedulePage
