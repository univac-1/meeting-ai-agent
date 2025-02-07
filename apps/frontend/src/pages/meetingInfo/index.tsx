import axios from "axios"
import { message, DatePicker, TimePicker, Button, Table } from "antd"
import { useEffect, useState } from "react"
import { version } from "../../../package.json"
import { useNavigate, useParams } from "react-router-dom"
import dayjs from "dayjs"
import { CloseOutlined } from "@ant-design/icons"

import styles from "./index.module.scss"
import logoSrc from "@/assets/login_logo.png"

import { CLOUD_RUN_ENDPOINT } from "@/config"
import { DocumentData, doc, getDoc } from "firebase/firestore"
import { db } from "@/firebase"

const MeetingInfoPage = () => {
  const nav = useNavigate()
  const { meetingId } = useParams<{ meetingId: string }>()
  const [messageApi, contextHolder] = message.useMessage()
  const [data, setData] = useState<DocumentData | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      if (!meetingId) {
        messageApi.error("会議IDが指定されていません")
        return
      }

      try {
        const docRef = doc(db, "meetings", meetingId)
        const docSnap = await getDoc(docRef)

        if (docSnap.exists()) {
          setData(docSnap.data())
        } else {
          messageApi.error("指定された会議は存在しません")
        }
      } catch (error) {
        console.error("データの取得中にエラーが発生しました:", error)
        messageApi.error("データの取得中にエラーが発生しました")
      }
    }

    fetchData()
  }, [meetingId])

  const agendaColumns = [
    {
      title: "トピック",
      dataIndex: "topic",
      key: "topic",
    },
    {
      title: "時間 (分)",
      dataIndex: "duration",
      key: "duration",
    },
  ]

  const dataSource = data
    ? [
        { key: "1", label: "会議ID", value: meetingId },
        { key: "2", label: "会議名", value: data.meeting_name },
        { key: "3", label: "目的", value: data.meeting_purpose },
        { key: "4", label: "開始日", value: data.start_date },
        { key: "5", label: "開始時刻", value: data.start_time },
        { key: "6", label: "終了時刻", value: data.end_time },
        {
          key: "7",
          label: "参加者",
          value: (
            <ul>
              {data.participants.map((participant: string, index: number) => (
                <li key={index}>{participant}</li>
              ))}
            </ul>
          ),
        },
        {
          key: "8",
          label: "アジェンダ",
          value: (
            <ul>
              {data.agenda.map((item: any, index: number) => (
                <li key={index}>
                  {item.topic} - {item.duration}分
                </li>
              ))}
            </ul>
          ),
        },
      ]
    : []

  const columns = [
    { title: "ラベル", dataIndex: "label", key: "label" },
    { title: "値", dataIndex: "value", key: "value" },
  ]

  return (
    <div className={styles.scheduleInfoPage}>
      {contextHolder}
      <section className={styles.content}>
        <div className={styles.title}>
          <div className={styles.logo}>
            <img src={logoSrc} alt="" />
          </div>
          <div className={styles.text}>Meeting Info</div>
        </div>
        <Table columns={columns} dataSource={dataSource} pagination={false} showHeader={false} />
        <div className={styles.btnWrapper}>
          <span className={styles.btnBack} onClick={() => nav("/")}>
            Back
          </span>
        </div>
      </section>
    </div>
  )
}

export default MeetingInfoPage
