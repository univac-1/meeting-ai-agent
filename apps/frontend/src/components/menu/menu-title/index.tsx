import { TranscriptionIcon, AiIcon, MinutesIcon } from "@/components/icons"
import { CloseOutlined } from "@ant-design/icons"
import { RootState } from "@/store"
import { useSelector, useDispatch } from "react-redux"
import React, { useEffect, useMemo, useRef, useState } from "react"
import { MenuType } from "@/types"
import {
  setAIShow,
  setMinutesShow,
  setDialogRecordShow,
  removeMenuItem,
  addMenuItem,
} from "@/store/reducers/global"

import styles from "./index.module.scss"

const MenuTitle = () => {
  const dispatch = useDispatch()
  const menuList = useSelector((state: RootState) => state.global.menuList)
  const activeType = menuList[0]

  const TitleOneText = useMemo(() => {
    if (activeType === "AI") {
      return "AI Assistant"
    } else if (activeType === "Minutes") {
      return "Minutes"
    } else {
      return "Conversation History"
    }
  }, [activeType])

  const onClickClose = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (activeType === "AI") {
      dispatch(setAIShow(false))
      dispatch(removeMenuItem("AI"))
    } else if (activeType === "Minutes") {
      dispatch(setMinutesShow(false))
      dispatch(removeMenuItem("Minutes"))
    } else {
      dispatch(setDialogRecordShow(false))
      dispatch(removeMenuItem("DialogRecord"))
    }
  }

  const onClickItem = (type: MenuType) => {
    dispatch(addMenuItem(type))
  }

  return (
    <div className={styles.title}>
      {menuList.length == 1 ? (
        <div className={styles.titleOne}>
          <TranscriptionIcon width={16} height={16}></TranscriptionIcon>
          <span className={styles.text}>{TitleOneText}</span>
          <CloseOutlined style={{ fontSize: "12px" }} onClick={onClickClose} />
        </div>
      ) : (
        <div className={styles.titleTwo}>
          {menuList.includes("DialogRecord") ? (
            <span
              className={`${styles.item} ${activeType == "DialogRecord" ? "active" : ""}`}
              onClick={() => onClickItem("DialogRecord")}
            >
              <TranscriptionIcon width={16} height={16}></TranscriptionIcon>
              <span className={styles.text}>Conversation History</span>
              {activeType == "DialogRecord" ? (
                <CloseOutlined style={{ fontSize: "12px" }} onClick={onClickClose} />
              ) : null}
            </span>
          ) : null}
          {menuList.includes("Minutes") ? (
            <span
              className={`${styles.item} ${activeType == "Minutes" ? "active" : ""}`}
              onClick={() => onClickItem("Minutes")}
            >
              <MinutesIcon width={16} height={16}></MinutesIcon>
              <span className={styles.text}>Minutes</span>
              {activeType == "Minutes" ? (
                <CloseOutlined style={{ fontSize: "12px" }} onClick={onClickClose} />
              ) : null}
            </span>
          ) : null}
          {menuList.includes("AI") ? (
            <span
              className={`${styles.item} ${activeType == "AI" ? "active" : ""}`}
              onClick={() => onClickItem("AI")}
            >
              <AiIcon width={16} height={16}></AiIcon>
              <span className={styles.text}>AI Assistant</span>
              {activeType == "AI" ? (
                <CloseOutlined style={{ fontSize: "12px" }} onClick={onClickClose} />
              ) : null}
            </span>
          ) : null}
        </div>
      )}
    </div>
  )
}

export default MenuTitle
