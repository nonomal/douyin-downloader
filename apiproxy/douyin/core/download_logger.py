#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下载日志记录器
记录每次下载任务的成功和失败清单
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading

class DownloadLogger:
    """下载日志记录器"""

    def __init__(self, download_dir: str):
        """
        初始化日志记录器

        Args:
            download_dir: 下载目录路径
        """
        self.download_dir = Path(download_dir)
        self.log_dir = self.download_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)

        # 当前会话的日志文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = timestamp
        self.log_file = self.log_dir / f"download_log_{timestamp}.json"
        self.summary_file = self.log_dir / f"download_summary_{timestamp}.txt"

        # 日志数据
        self.log_data = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "statistics": {
                "total_tasks": 0,
                "successful": 0,
                "failed": 0,
                "skipped": 0,
                "success_rate": 0.0,
                "total_time": 0
            },
            "successful_downloads": [],
            "failed_downloads": [],
            "skipped_downloads": []
        }

        # 线程锁
        self.lock = threading.Lock()

        # 初始化日志文件
        self._save_log()

    def add_success(self, task_info: Dict[str, Any]):
        """
        记录成功的下载

        Args:
            task_info: 任务信息字典，包含url, title, file_path等
        """
        with self.lock:
            record = {
                "timestamp": datetime.now().isoformat(),
                "url": task_info.get("url", ""),
                "title": task_info.get("title", ""),
                "file_path": task_info.get("file_path", ""),
                "file_size": task_info.get("file_size", 0),
                "download_time": task_info.get("download_time", 0),
                "video_id": task_info.get("video_id", "")
            }

            self.log_data["successful_downloads"].append(record)
            self.log_data["statistics"]["successful"] += 1
            self.log_data["statistics"]["total_tasks"] += 1
            self._update_success_rate()
            self._save_log()

    def add_failure(self, task_info: Dict[str, Any]):
        """
        记录失败的下载

        Args:
            task_info: 任务信息字典，包含url, error_message等
        """
        with self.lock:
            record = {
                "timestamp": datetime.now().isoformat(),
                "url": task_info.get("url", ""),
                "title": task_info.get("title", ""),
                "error_message": task_info.get("error_message", ""),
                "error_type": task_info.get("error_type", ""),
                "retry_count": task_info.get("retry_count", 0),
                "video_id": task_info.get("video_id", "")
            }

            self.log_data["failed_downloads"].append(record)
            self.log_data["statistics"]["failed"] += 1
            self.log_data["statistics"]["total_tasks"] += 1
            self._update_success_rate()
            self._save_log()

    def add_skipped(self, task_info: Dict[str, Any]):
        """
        记录跳过的下载（已存在的文件）

        Args:
            task_info: 任务信息字典
        """
        with self.lock:
            record = {
                "timestamp": datetime.now().isoformat(),
                "url": task_info.get("url", ""),
                "title": task_info.get("title", ""),
                "reason": task_info.get("reason", "文件已存在"),
                "existing_file": task_info.get("existing_file", ""),
                "video_id": task_info.get("video_id", "")
            }

            self.log_data["skipped_downloads"].append(record)
            self.log_data["statistics"]["skipped"] += 1
            self.log_data["statistics"]["total_tasks"] += 1
            self._save_log()

    def _update_success_rate(self):
        """更新成功率"""
        total_processed = (self.log_data["statistics"]["successful"] +
                          self.log_data["statistics"]["failed"])
        if total_processed > 0:
            self.log_data["statistics"]["success_rate"] = (
                self.log_data["statistics"]["successful"] / total_processed * 100
            )

    def _save_log(self):
        """保存日志到文件"""
        try:
            # 保存JSON格式的详细日志
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.log_data, f, ensure_ascii=False, indent=2)

            # 同时生成人类可读的摘要文件
            self._save_summary()
        except Exception as e:
            print(f"保存日志失败: {e}")

    def _save_summary(self):
        """保存人类可读的摘要"""
        try:
            with open(self.summary_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"下载任务摘要报告\n")
                f.write(f"会话ID: {self.session_id}\n")
                f.write(f"开始时间: {self.log_data['start_time']}\n")
                f.write("=" * 80 + "\n\n")

                # 统计信息
                stats = self.log_data["statistics"]
                f.write("【统计信息】\n")
                f.write(f"总任务数: {stats['total_tasks']}\n")
                f.write(f"成功: {stats['successful']}\n")
                f.write(f"失败: {stats['failed']}\n")
                f.write(f"跳过: {stats['skipped']}\n")
                f.write(f"成功率: {stats['success_rate']:.1f}%\n\n")

                # 成功列表
                if self.log_data["successful_downloads"]:
                    f.write("【成功下载列表】\n")
                    for i, item in enumerate(self.log_data["successful_downloads"], 1):
                        f.write(f"{i}. {item.get('title', '未知标题')}\n")
                        f.write(f"   URL: {item['url']}\n")
                        f.write(f"   文件: {item.get('file_path', '未知')}\n")
                        f.write(f"   大小: {self._format_size(item.get('file_size', 0))}\n")
                        f.write(f"   耗时: {item.get('download_time', 0):.1f}秒\n\n")

                # 失败列表
                if self.log_data["failed_downloads"]:
                    f.write("\n【失败下载列表】\n")
                    for i, item in enumerate(self.log_data["failed_downloads"], 1):
                        f.write(f"{i}. {item.get('title', '未知标题')}\n")
                        f.write(f"   URL: {item['url']}\n")
                        f.write(f"   错误: {item.get('error_message', '未知错误')}\n")
                        f.write(f"   重试次数: {item.get('retry_count', 0)}\n\n")

                # 跳过列表
                if self.log_data["skipped_downloads"]:
                    f.write("\n【跳过下载列表】\n")
                    for i, item in enumerate(self.log_data["skipped_downloads"], 1):
                        f.write(f"{i}. {item.get('title', '未知标题')}\n")
                        f.write(f"   URL: {item['url']}\n")
                        f.write(f"   原因: {item.get('reason', '未知')}\n\n")

        except Exception as e:
            print(f"保存摘要失败: {e}")

    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def finalize(self, total_time: float = 0):
        """
        完成日志记录

        Args:
            total_time: 总耗时（秒）
        """
        with self.lock:
            self.log_data["end_time"] = datetime.now().isoformat()
            self.log_data["statistics"]["total_time"] = total_time
            self._save_log()

            # 打印最终统计
            print("\n" + "=" * 60)
            print("下载任务完成统计")
            print("=" * 60)
            stats = self.log_data["statistics"]
            print(f"总任务数: {stats['total_tasks']}")
            print(f"成功: {stats['successful']}")
            print(f"失败: {stats['failed']}")
            print(f"跳过: {stats['skipped']}")
            print(f"成功率: {stats['success_rate']:.1f}%")
            print(f"总耗时: {total_time:.1f}秒")
            print(f"\n日志文件已保存至:")
            print(f"  详细日志: {self.log_file}")
            print(f"  摘要报告: {self.summary_file}")
            print("=" * 60)

    def get_statistics(self) -> Dict[str, Any]:
        """获取当前统计信息"""
        with self.lock:
            return self.log_data["statistics"].copy()