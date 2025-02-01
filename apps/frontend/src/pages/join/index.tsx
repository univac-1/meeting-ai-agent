import { Switch, Input, message } from "antd"
import { useSelector, useDispatch } from "react-redux"
import { RootState } from "@/store"
import { InputStatuses } from "@/types"
import { useState, useRef, useEffect, useCallback, useMemo } from "react"
import { genRandomUserId, REGEX_SPECIAL_CHAR, GITHUB_URL, parseQuery } from "@/common"
import { setOptions, setUserInfo, setMeetingId } from "@/store/reducers/global"
import { version } from "../../../package.json"
import { useNavigate, useLocation } from "react-router-dom"

import styles from "./index.module.scss"
import logoSrc from "@/assets/login_logo.png"
import githubSrc from "@/assets/github.jpg"

const JoinPage = () => {
  const nav = useNavigate()
  const location = useLocation()
  const dispatch = useDispatch()
  const [messageApi, contextHolder] = message.useMessage()
  const options = useSelector((state: RootState) => state.global.options)
  const [channel, setChannel] = useState("")
  const [userName, setUserName] = useState("")
  const [channelInputStatuses, setChannelInputStatuses] = useState<InputStatuses>("")

  const onChangeChannel = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value
    if (REGEX_SPECIAL_CHAR.test(value)) {
      setChannelInputStatuses("error")
      value = value.replace(REGEX_SPECIAL_CHAR, "")
    } else {
      setChannelInputStatuses("")
    }
    setChannel(value)
  }

  const onChangeUserName = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value
    if (REGEX_SPECIAL_CHAR.test(value)) {
      value = value.replace(REGEX_SPECIAL_CHAR, "")
    }
    setUserName(value)
  }

  const onClickJoin = () => {
    if (!channel) {
      return messageApi.error("please enter channel name!")
    }
    if (!userName) {
      return messageApi.error("please enter user name!")
    }
    dispatch(setOptions({ channel }))
    dispatch(setMeetingId(channel))
    dispatch(
      setUserInfo({
        userName,
        userId: genRandomUserId(),
      }),
    )
    if (location.search) {
      nav(`/meeting?${location.search.slice(1)}`)
    } else {
      nav("/meeting")
    }
  }

  const onClickGithub = () => {
    window.open(GITHUB_URL, "_blank")
  }

  return (
    <div className={styles.joinPage}>
      {contextHolder}
      <section className={styles.content}>
        <div className={styles.title}>
          <div className={styles.logo}>
            <img src={logoSrc} alt="" />
          </div>
          <div className={styles.text}>Join Meeting</div>
        </div>
        <div className={styles.item}>
          <Input
            status={channelInputStatuses}
            allowClear
            placeholder="please enter channel name"
            onChange={onChangeChannel}
            value={channel}
          />
        </div>
        <div className={styles.item}>
          <Input
            allowClear
            placeholder="please enter user name"
            onChange={onChangeUserName}
            value={userName}
          />
        </div>
        <div className={styles.btn} onClick={onClickJoin}>
          Join Meeting
        </div>
      </section>
    </div>
  )
}

export default JoinPage
