import axios from "axios"
import { Input, message, DatePicker, TimePicker, Button } from "antd"
import { useState } from "react"
import { version } from "../../../package.json"
import { useNavigate } from "react-router-dom"
import { CLOUD_RUN_ENDPOINT } from "@/config"
import dayjs from "dayjs"
import { CloseOutlined } from "@ant-design/icons"

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
      setAgendaItems([
        ...agendaItems,
        { topic: agendaInput.trim(), duration: durationInput.trim() },
      ])
      setAgendaInput("")
      setDurationInput("")
    }
  }

  const removeAgendaItem = (index: number) => {
    setAgendaItems(agendaItems.filter((_, i) => i !== index))
  }

  const handleApiCall = async () => {
    if (!meetingName.trim()) {
      messageApi.error("Meeting Name is required.")
      return
    }
    if (!meetingPurpose.trim()) {
      messageApi.error("Meeting Purpose is required.")
      return
    }
    if (!startDate) {
      messageApi.error("Start Date is required.")
      return
    }
    if (!startTime) {
      messageApi.error("Start Time is required.")
      return
    }
    if (!endTime) {
      messageApi.error("End Time is required.")
      return
    }
    if (participants.length === 0) {
      messageApi.error("At least one participant is required.")
      return
    }
    if (agendaItems.length === 0) {
      messageApi.error("At least one agenda item is required.")
      return
    }

    try {
      const response = await axios.post(`${CLOUD_RUN_ENDPOINT}/meeting`, {
        meeting_name: meetingName,
        meeting_purpose: meetingPurpose,
        start_date: startDate.format("YYYY-MM-DD"),
        start_time: startTime.format("HH:mm"),
        end_time: endTime.format("HH:mm"),
        participants,
        agenda: agendaItems.map((item) => ({ topic: item.topic, duration: item.duration })),
      })

      const meetingId = response.data?.data?.meeting_id
      if (meetingId) {
        messageApi.success("Meeting scheduled successfully!")
        nav(`/meeting/${meetingId}`)
      } else {
        throw new Error("Meeting ID is undefined")
      }
    } catch (error) {
      console.error("Error calling API:", error)
      messageApi.error("Failed to schedule meeting.")
    }
  }

  const onClickSave = () => {
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
          <div className={styles.text}>Schedule Meeting</div>
        </div>
        <div className={styles.item}>
          <label>Meeting Name</label>
          <Input
            allowClear
            placeholder="Enter meeting name"
            onChange={(e) => setMeetingName(e.target.value)}
            value={meetingName}
          />
        </div>
        <div className={styles.item}>
          <label>Meeting Purpose</label>
          <TextArea
            allowClear
            placeholder="Enter meeting purpose"
            onChange={(e) => setMeetingPurpose(e.target.value)}
            value={meetingPurpose}
            rows={4}
          />
        </div>
        <div className={styles.item}>
          <label>Start Date</label>
          <DatePicker
            style={{ width: "100%" }}
            placeholder="Select start date"
            onChange={(date) => setStartDate(date)}
            value={startDate}
          />
        </div>
        <div className={styles.item}>
          <label>Start Time</label>
          <TimePicker
            style={{ width: "100%" }}
            format="HH:mm"
            placeholder="Select start time"
            onChange={(time) => setStartTime(time)}
            value={startTime}
          />
        </div>
        <div className={styles.item}>
          <label>End Time</label>
          <TimePicker
            style={{ width: "100%" }}
            format="HH:mm"
            placeholder="Select end time"
            onChange={(time) => setEndTime(time)}
            value={endTime}
          />
        </div>
        <div className={styles.item}>
          <label>Participants</label>
          <Input
            allowClear
            placeholder="Enter participant and press Enter"
            onChange={onParticipantInputChange}
            onKeyPress={onParticipantInputKeyPress}
            value={participantInput}
          />
        </div>
        <div className={styles.item}>
          {participants.map((participant, index) => (
            <div key={index} style={{ display: "flex", alignItems: "center" }}>
              <span style={{ flexGrow: 1 }}>{participant}</span>
              <Button
                type="link"
                icon={<CloseOutlined />}
                onClick={() => removeParticipant(index)}
              />
            </div>
          ))}
        </div>
        <div className={styles.item}>
          <label>Agenda</label>
          <Input
            allowClear
            placeholder="Enter agenda and press Enter"
            onChange={onAgendaInputChange}
            onKeyPress={onAgendaInputKeyPress}
            value={agendaInput}
          />
        </div>
        <div className={styles.item}>
          <label>Agenda Duration (minutes)</label>
          <Input
            allowClear
            type="number"
            placeholder="Enter agenda duration and press Enter"
            onChange={onDurationInputChange}
            onKeyPress={onAgendaInputKeyPress}
            value={durationInput}
          />
        </div>
        <div className={styles.agendaList}>
          {agendaItems.map((item, index) => (
            <div key={index} style={{ display: "flex", alignItems: "center" }}>
              <span style={{ flexGrow: 1 }}>
                {item.topic} - {item.duration} minutes
              </span>
              <Button
                type="link"
                icon={<CloseOutlined />}
                onClick={() => removeAgendaItem(index)}
              />
            </div>
          ))}
        </div>
        <div className={styles.btnWrapper}>
          <span className={styles.btnCancel} onClick={onClickCancel}>
            Cancel
          </span>
          <span className={styles.btnSave} onClick={onClickSave}>
            Save
          </span>
        </div>
      </section>
    </div>
  )
}

export default MeetingSchedulePage
