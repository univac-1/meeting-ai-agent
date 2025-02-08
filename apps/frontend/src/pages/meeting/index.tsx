// speech recognition
import "core-js/stable"
import "regenerator-runtime/runtime"
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition"

import { useMount, useMessage } from "@/common"
import { IUserInfo, IUserData, ILanguageSelect, ISttData, ICommentItem } from "@/types"

import {
  RtcManager,
  RtmManager,
  ISimpleUserInfo,
  IUserTracks,
  IRtcUser,
  SttManager,
  ITextstream,
} from "@/manager"
import Header from "../../components/header"
import Footer from "../../components/footer"
import CenterArea from "../../components/center-area"
import UserList from "../../components/user-list"
import Caption from "../../components/caption"
import Menu from "../../components/menu"
import { RootState } from "@/store"
import {
  setLocalAudioMute,
  setLocalVideoMute,
  setLanguageSelect,
  reset,
  setCaptionShow,
  addMessage,
  updateSubtitles,
  setSttData,
  setSubtitles,
  setRecordLanguageSelect,
  setChatHistory,
} from "@/store/reducers/global"
import { useSelector, useDispatch } from "react-redux"
import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import axios from "axios"

// firebase
import { CLOUD_RUN_ENDPOINT } from "@/config"
import { db } from "@/firebase"
import { collection, onSnapshot, orderBy, query, doc } from "firebase/firestore"

// antd
import { Button, notification, Space } from "antd"

// icon
import { AiIcon } from "@/components/icons"

import styles from "./index.module.scss"

const rtcManager = new RtcManager()
const rtmManager = new RtmManager()
const sttManager = new SttManager({
  rtmManager,
})

window.rtcManager = rtcManager
window.rtmManager = rtmManager
window.sttManager = sttManager

type StatusType = "init" | "recording" | "ready"

const MeetingPage = () => {
  const dispatch = useDispatch()
  const nav = useNavigate()
  const isMounted = useMount()
  const localAudioMute = useSelector((state: RootState) => state.global.localAudioMute)
  const localVideoMute = useSelector((state: RootState) => state.global.localVideoMute)
  const userInfo = useSelector((state: RootState) => state.global.userInfo)
  const options = useSelector((state: RootState) => state.global.options)
  const memberListShow = useSelector((state: RootState) => state.global.memberListShow)
  const dialogRecordShow = useSelector((state: RootState) => state.global.dialogRecordShow)
  const captionShow = useSelector((state: RootState) => state.global.captionShow)
  const minutesShow = useSelector((state: RootState) => state.global.minutesShow)
  const aiShow = useSelector((state: RootState) => state.global.aiShow)
  const sttData = useSelector((state: RootState) => state.global.sttData)
  const { userId, userName } = userInfo
  const { channel } = options
  const [localTracks, setLocalTracks] = useState<IUserTracks>()
  const [userRtmList, setRtmUserList] = useState<ISimpleUserInfo[]>([])
  const [rtcUserMap, setRtcUserMap] = useState<Map<number | string, IRtcUser>>(new Map())
  const [centerUserId, setCenterUserId] = useState(userInfo.userId)

  // notification
  const [api, contextHolder] = notification.useNotification()

  const meetingId = useSelector((state: RootState) => state.global.meetingId)
  const initialLoadRef = useRef(true)

  const { transcript, listening, browserSupportsSpeechRecognition } = useSpeechRecognition()

  const [status, setStatus] = useState<StatusType>("init")

  // 以下、MediaRecorder 関連のインスタンスを useRef で保持
  const streamRef = useRef<MediaStream | null>(null)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const audioDataRef = useRef<Blob[]>([])

  // APIキーやメッセージ送信 API のエンドポイント（適宜修正）
  const GOOGLE_API_KEY = import.meta.env.VITE_GOOGLE_API_KEY

  // init
  useEffect(() => {
    if (!userInfo.userId) {
      dispatch(addMessage({ content: "Please login first", type: "error" }))
      nav("/")
    }
    startVoiceRecognition()
    init()

    return () => {
      destory()
      stopVoiceRecognition()
    }
  }, [])

  // 通知を表示する
  const openNotification = () => {
    console.log("openNotification")
    const key = `open${Date.now()}`
    const btn = (
      <Space>
        <Button
          type="link"
          size="small"
          onClick={() => {
            handleGetAIOpinion()
            api.destroy()
          }}
        >
          Get AI's Opinion
        </Button>
      </Space>
    )
    api.open({
      message: "AIエージェントから意見があります",
      description: "発言を許可する場合は「Get AI's Opinion」ボタンをクリックしてください。",
      placement: "bottom",
      duration: 0,
      icon: <AiIcon></AiIcon>,
      btn,
      key,
    })
  }

  const handleGetAIOpinion = async () => {
    try {
      const response = await axios.get(`${CLOUD_RUN_ENDPOINT}/meeting/${channel}/intervention`)
      console.log(response.data)
    } catch (error) {
      console.error("Error:", error)
    }
  }

  useEffect(() => {
    if (!channel) return

    const docRef = doc(db, "meetings", channel)
    const unsubscribe = onSnapshot(
      docRef,
      (docSnapshot) => {
        if (docSnapshot.exists()) {
          const data = docSnapshot.data()
          console.log("ドキュメントが更新されました:", data)

          // intervention_request.statusが"pending"の場合の処理
          if (data.intervention_request?.status === "pending") {
            console.log("介入リクエストがペンディング状態になりました。")
            openNotification()
          }
        } else {
          console.log("ドキュメントが存在しません")
        }
      },
      (error) => {
        console.error("サブスクライブ中にエラーが発生しました:", error)
      },
    )

    return () => unsubscribe()
  }, [channel])

  // 音声合成などのための補助関数
  const base64ToBlob = (base64Data: string, contentType: string): Blob => {
    const byteCharacters = atob(base64Data)
    const byteArrays: Uint8Array[] = []
    for (let offset = 0; offset < byteCharacters.length; offset += 512) {
      const slice = byteCharacters.slice(offset, offset + 512)
      const byteNumbers: number[] = new Array(slice.length)
      for (let i = 0; i < slice.length; i++) {
        byteNumbers[i] = slice.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      byteArrays.push(byteArray)
    }
    return new Blob(byteArrays, { type: contentType })
  }

  const handleTextToSpeech = async (text: string): Promise<void> => {
    try {
      const response = await fetch(
        `https://texttospeech.googleapis.com/v1/text:synthesize?key=${GOOGLE_API_KEY}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            input: { text },
            voice: {
              languageCode: "ja-JP",
              ssmlGender: "NEUTRAL",
            },
            audioConfig: {
              audioEncoding: "MP3",
              speakingRate: "1.5",
              volumeGainDb: "-90.0",
            },
          }),
        },
      )

      const data = await response.json()
      if (data.audioContent) {
        const audioBlob = base64ToBlob(data.audioContent, "audio/mp3")
        const url = URL.createObjectURL(audioBlob)
        const audio = new Audio(url)
        await audio.play()
      }
    } catch (error) {
      console.error("音声合成に失敗した:", error)
    }
  }

  // AIコメント処理関数群
  const handleEvaluation = (aiComment: ICommentItem) => {
    console.log("評価コメントを処理します:", aiComment.message)
    // 評価に関する追加処理があればここに記述
  }

  const handleSummary = (aiComment: ICommentItem) => {
    console.log("要約コメントを処理します:", aiComment.message)
    // 要約に関する追加処理があればここに記述
  }

  const handleFeedback = (aiComment: ICommentItem) => {
    console.log("フィードバックコメントを処理します:", aiComment.message)
    // 音声読み上げ処理を実行する
    handleTextToSpeech(aiComment.message)
  }

  const handleAIComment = (aiComment: ICommentItem) => {
    if (!aiComment.meta || !aiComment.meta.type) {
      console.warn("AIコメントのタイプが不明です:", aiComment)
      return
    }
    switch (aiComment.meta.type) {
      case "evaluation":
        handleEvaluation(aiComment)
        break
      case "summary":
        handleSummary(aiComment)
        break
      case "feedback":
        handleFeedback(aiComment)
        break
      default:
        console.warn("未対応のAIコメントタイプです:", aiComment.meta.type)
    }
  }

  // メッセージ履歴の取得およびAIコメントの検出処理
  useEffect(() => {
    if (!meetingId) return
    const commentsRef = collection(db, "meetings", meetingId, "comments")
    const q = query(commentsRef, orderBy("speak_at"))

    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      // 全ドキュメントからメッセージ履歴を構築
      const messageHistory: ICommentItem[] = querySnapshot.docs.map((doc) => {
        const data = doc.data() as ICommentItem
        data.speaker = data.speaker.toString()
        return data
      })

      // 追加されたドキュメントに対してのみ処理
      querySnapshot.docChanges().forEach((change) => {
        if (change.type === "added") {
          const data = change.doc.data() as ICommentItem
          data.speaker = data.speaker.toString()
          if (!initialLoadRef.current && data?.meta && data?.meta?.role === "ai") {
            handleAIComment(data)
          }
        }
      })

      if (initialLoadRef.current) {
        initialLoadRef.current = false
      }
      dispatch(setChatHistory(messageHistory))
    })

    return () => unsubscribe()
  }, [meetingId])

  // useSpeechRecognition による listening の変化に合わせ、録音開始／停止する
  useEffect(() => {
    if (!browserSupportsSpeechRecognition) {
      console.warn("Browser doesn't support speech recognition.")
      return
    }
    if (listening) {
      console.log("[useEffect] listening true 発話開始検知 → startRecording")
      startRecording()
    } else {
      console.log("[useEffect] listening false 発話終了検知 → stopRecording")
      stopRecording()
    }
  }, [listening, browserSupportsSpeechRecognition])

  // localAudioMute による SpeechRecognition の開始／停止制御
  useEffect(() => {
    if (!browserSupportsSpeechRecognition) {
      console.warn("Browser doesn't support speech recognition.")
      return
    }

    if (!localAudioMute) {
      if (!listening) {
        SpeechRecognition.startListening()
      }
    } else {
      if (listening) {
        SpeechRecognition.stopListening()
      }
    }
  }, [localAudioMute, listening, browserSupportsSpeechRecognition])

  // useSpeechRecognition の transcript の変化によるメッセージ送信（既存処理）
  useEffect(() => {
    if (!localAudioMute && transcript) {
      console.log("[WebSpeechAPI] 認識結果:", transcript)
      // axios
      //   .post(
      //     `${CLOUD_RUN_ENDPOINT}/message`,
      //     {
      //       meeting_id: channel,
      //       speaker: userName,
      //       message: transcript,
      //     },
      //     {
      //       headers: {
      //         "Content-type": "application/json; charset=UTF-8",
      //       },
      //     }
      //   )
      //   .then((response) => console.log("[message] 送信成功:", response.data))
      //   .catch((error) => console.error("[message] エラー:", error))
    }
  }, [listening, localAudioMute])

  const simpleUserMap: Map<number | string, IUserInfo> = useMemo(() => {
    const map = new Map<number | string, IUserInfo>()
    for (let i = 0; i < userRtmList.length; i++) {
      const item = userRtmList[i]
      const userId = Number(item.userId)
      map.set(userId, {
        userId,
        userName: item.userName,
      })
    }
    map.set(userInfo.userId, {
      userId: userInfo.userId,
      userName: userInfo.userName,
    })

    return map
  }, [userRtmList, userInfo])

  // listen events
  useEffect(() => {
    window.rtmManager.on("userListChanged", onRtmUserListChanged)
    window.rtmManager.on("languagesChanged", onLanguagesChanged)
    window.rtmManager.on("sttDataChanged", onSttDataChanged)
    window.rtcManager.on("localUserChanged", onLocalUserChanged)
    window.rtcManager.on("remoteUserChanged", onRemoteUserChanged)
    window.rtcManager.on("textstreamReceived", onTextStreamReceived)

    return () => {
      window.rtmManager.off("userListChanged", onRtmUserListChanged)
      window.rtmManager.off("languagesChanged", onLanguagesChanged)
      window.rtmManager.off("sttDataChanged", onSttDataChanged)
      window.rtcManager.off("localUserChanged", onLocalUserChanged)
      window.rtcManager.off("remoteUserChanged", onRemoteUserChanged)
      window.rtcManager.off("textstreamReceived", onTextStreamReceived)
    }
  }, [simpleUserMap])

  useEffect(() => {
    localTracks?.videoTrack?.setMuted(localVideoMute)
  }, [localTracks?.videoTrack, localVideoMute])

  useEffect(() => {
    localTracks?.audioTrack?.setMuted(localAudioMute)
  }, [localTracks?.audioTrack, localAudioMute])

  const userDataList = useMemo(() => {
    const list: IUserData[] = []

    for (const item of simpleUserMap.values()) {
      const userId = item.userId
      const rtcUser = rtcUserMap.get(userId)
      const isCenterUser = userId === centerUserId
      const isLocalUser = userId === userInfo.userId
      list.push({
        userId,
        isLocal: isLocalUser,
        order: isCenterUser ? 1000 : 1,
        userName: item.userName,
        videoTrack: isLocalUser ? localTracks?.videoTrack : rtcUser?.videoTrack,
        audioTrack: isLocalUser ? localTracks?.audioTrack : rtcUser?.audioTrack,
      })
    }
    return list.sort((a, b) => b.order - a.order)
  }, [simpleUserMap, userInfo, localTracks, centerUserId, rtcUserMap])

  const curUserData = useMemo(() => {
    return userDataList[0] as IUserData
  }, [userDataList])

  const init = async () => {
    await Promise.all([
      rtcManager.createTracks(),
      rtcManager.join({
        userId,
        channel,
      }),
      sttManager.init({
        userId: userId + "",
        userName,
        channel,
      }),
    ])
    await rtcManager.publish()
  }

  const destory = async () => {
    await Promise.all([rtcManager.destroy(), sttManager.destroy()])
    dispatch(reset())
  }

  const onLocalUserChanged = (tracks: IUserTracks) => {
    setLocalTracks(tracks)
    if (tracks.videoTrack) {
      dispatch(setLocalVideoMute(false))
    }
    if (tracks.audioTrack) {
      dispatch(setLocalAudioMute(false))
    }
  }

  const onRtmUserListChanged = (list: ISimpleUserInfo[]) => {
    console.log("[test] onRtmUserListChanged", list)
    setRtmUserList(list)
  }

  const onRemoteUserChanged = (user: IRtcUser) => {
    setRtcUserMap((prev) => {
      const newMap = new Map(prev)
      newMap.set(Number(user.userId), user)
      return newMap
    })
  }

  const onSttDataChanged = (data: ISttData) => {
    console.log("[test] onSttDataChanged", data)
    dispatch(setSttData(data))
  }

  const onTextStreamReceived = (textstream: ITextstream) => {
    // modify subtitle list
    const targetUser = simpleUserMap.get(Number(textstream.uid))
    dispatch(updateSubtitles({ textstream, username: targetUser?.userName || "" }))
  }

  const onLanguagesChanged = (languages: ILanguageSelect) => {
    console.log("[test] onLanguagesChanged", languages)
    dispatch(setLanguageSelect(languages))
  }

  const onClickUserListItem = (data: IUserData) => {
    setCenterUserId(data.userId)
  }

  /**
   * マイクからのストリーム取得後に MediaRecorder を初期化する
   */
  const startVoiceRecognition = async (): Promise<void> => {
    try {
      const stream: MediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
        },
      })
      streamRef.current = stream
      initializeRecorder()
      setStatus("ready")
    } catch (error) {}
  }

  /**
   * MediaRecorder の初期化処理
   */
  const initializeRecorder = (): void => {
    if (!streamRef.current) return
    const recorder = new MediaRecorder(streamRef.current)
    recorderRef.current = recorder
    audioDataRef.current = []
    recorder.addEventListener("dataavailable", (event: BlobEvent) => {
      audioDataRef.current.push(event.data)
    })
    recorder.addEventListener("stop", handleRecordingStop)
  }

  /**
   * 録音開始処理
   */
  const startRecording = (): void => {
    if (!recorderRef.current) return
    audioDataRef.current = []
    try {
      recorderRef.current.start()
      setStatus("recording")
    } catch (error) {}
  }

  /**
   * 録音停止処理
   */
  const stopRecording = (): void => {
    if (!recorderRef.current || recorderRef.current.state !== "recording") return
    try {
      recorderRef.current.stop()
      setStatus("ready")
    } catch (error) {}
  }

  /**
   * 録音停止時の処理
   * 録音された Blob を Base64 に変換し、Google Cloud Speech-to-Text API へ送信する
   */
  const handleRecordingStop = (): void => {
    const audioBlob: Blob = new Blob(audioDataRef.current)
    const reader = new FileReader()
    reader.onload = () => {
      if (reader.result instanceof ArrayBuffer) {
        const uint8Array = new Uint8Array(reader.result)
        const base64Audio = arrayBufferToBase64(uint8Array)
        googleCloudSpeechToTextAPI(base64Audio)
      }
    }
    reader.readAsArrayBuffer(audioBlob)
  }

  /**
   * ArrayBuffer を Base64 に変換する処理
   */
  const arrayBufferToBase64 = (buffer: ArrayBuffer | Uint8Array): string => {
    let binary = ""
    const bytes = new Uint8Array(buffer)
    const len = bytes.byteLength
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    const base64 = window.btoa(binary)
    return base64
  }

  /**
   * Google Cloud Speech-to-Text API へ録音データを送信する
   */
  const googleCloudSpeechToTextAPI = async (base64Audio: string): Promise<void> => {
    const content = {
      config: {
        languageCode: "ja-JP",
        sampleRateHertz: 44100,
        encoding: "MP3",
        enableAutomaticPunctuation: true,
        model: "default",
      },
      audio: {
        content: base64Audio,
      },
    }

    try {
      const response = await fetch(
        `https://speech.googleapis.com/v1/speech:recognize?key=${GOOGLE_API_KEY}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json; charset=utf-8",
          },
          body: JSON.stringify(content),
        },
      )
      const resultJson = await response.json()
      const resultTranscript = resultJson.results?.[0]?.alternatives?.[0]?.transcript || ""
      console.log("[googleCloudSpeechToTextAPI] 認識結果:", resultTranscript)
      if (resultTranscript) {
        sendMessage(resultTranscript)
      }
    } catch (error) {
      console.error("[googleCloudSpeechToTextAPI] エラー:", error)
    }
  }

  /**
   * 取得したテキストを既存のメッセージ送信 API に渡す処理
   */
  const sendMessage = async (text: string): Promise<void> => {
    axios
      .post(
        `${CLOUD_RUN_ENDPOINT}/message`,
        {
          meeting_id: channel,
          speaker: userName,
          message: text,
        },
        {
          headers: { "Content-type": "application/json; charset=UTF-8" },
        },
      )
      .then((response) => {
        console.log("[sendMessage] メッセージ送信成功", response.data)
      })
      .catch((error) => {
        console.error("[sendMessage] メッセージ送信エラー:", error)
      })
  }

  /**
   * 音声認識および録音を完全に停止する処理
   */
  const stopVoiceRecognition = (): void => {
    console.log("[stopVoiceRecognition] 停止処理開始")
    if (recorderRef.current && recorderRef.current.state === "recording") {
      recorderRef.current.stop()
      console.log("[stopVoiceRecognition] 録音停止")
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop())
      console.log("[stopVoiceRecognition] ストリーム停止")
    }
    setStatus("init")
  }

  return (
    <div className={styles.meetingPage}>
      {contextHolder}
      <Header style={{ flex: "0 0 48px" }} />
      <section className={styles.content}>
        {memberListShow ? (
          <div className={styles.left}>
            <UserList data={userDataList.slice(1)} onClickItem={onClickUserListItem}></UserList>
          </div>
        ) : null}
        <section className={styles.center}>
          <CenterArea data={curUserData}></CenterArea>
        </section>
        {dialogRecordShow || aiShow || minutesShow ? (
          <section className={styles.right}>
            <Menu></Menu>
          </section>
        ) : null}
      </section>
      <Footer style={{ flex: "0 0 80px" }} />
      <Caption visible={captionShow}></Caption>
    </div>
  )
}

export default MeetingPage
