def build_order_summary_flex(user_data: dict):
    return {
        "type": "flex",
        "altText": "訂單摘要",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    { "type": "text", "text": "麻糬訂單確認", "weight": "bold", "size": "lg" }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    { "type": "text", "text": f"口味：{user_data.get('flavor', '未知')}" },
                    { "type": "text", "text": f"數量：{user_data.get('quantity', '未知')} 顆" },
                    { "type": "text", "text": f"姓名：{user_data.get('name', '')}" },
                    { "type": "text", "text": f"電話：{user_data.get('phone', '')}" },
                    { "type": "text", "text": f"地址：{user_data.get('address', '')}" }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "message",
                            "label": "確認送出",
                            "text": "確認送出訂單"
                        }
                    }
                ]
            }
        }
    }

def create_flavor_selection():
    """Create a flex message for flavor selection"""
    return {
        "type": "flex",
        "altText": "選擇口味",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    { "type": "text", "text": "請選擇麻糬口味", "weight": "bold", "size": "lg" }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "message",
                            "label": "紅豆",
                            "text": "Red Bean"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "message",
                            "label": "花生",
                            "text": "Peanut"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "message",
                            "label": "芝麻",
                            "text": "Sesame"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "message",
                            "label": "芋頭",
                            "text": "Taro"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "message",
                            "label": "紫米",
                            "text": "Purple Rice"
                        }
                    }
                ]
            }
        }
    }

def create_quantity_selection():
    """Create a flex message for quantity selection"""
    return {
        "type": "flex",
        "altText": "選擇數量",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    { "type": "text", "text": "請選擇數量", "weight": "bold", "size": "lg" }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "message",
                            "label": "6個",
                            "text": "6"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "message",
                            "label": "12個",
                            "text": "12"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "message",
                            "label": "20個",
                            "text": "20"
                        }
                    }
                ]
            }
        }
    } 