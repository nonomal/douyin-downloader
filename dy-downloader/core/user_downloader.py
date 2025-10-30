from typing import Any, Dict

from core.downloader_base import BaseDownloader, DownloadResult
from utils.logger import setup_logger

logger = setup_logger('UserDownloader')


class UserDownloader(BaseDownloader):
    async def download(self, parsed_url: Dict[str, Any]) -> DownloadResult:
        result = DownloadResult()

        sec_uid = parsed_url.get('sec_uid')
        if not sec_uid:
            logger.error("No sec_uid found in parsed URL")
            return result

        user_info = await self.api_client.get_user_info(sec_uid)
        if not user_info:
            logger.error(f"Failed to get user info: {sec_uid}")
            return result

        modes = self.config.get('mode', ['post'])

        for mode in modes:
            if mode == 'post':
                mode_result = await self._download_user_post(sec_uid, user_info)
                result.total += mode_result.total
                result.success += mode_result.success
                result.failed += mode_result.failed
                result.skipped += mode_result.skipped
            elif mode == 'like':
                mode_result = await self._download_user_like(sec_uid, user_info)
                result.total += mode_result.total
                result.success += mode_result.success
                result.failed += mode_result.failed
                result.skipped += mode_result.skipped
            elif mode == 'mix' or mode == 'allmix':
                mode_result = await self._download_user_mix(sec_uid, user_info)
                result.total += mode_result.total
                result.success += mode_result.success
                result.failed += mode_result.failed
                result.skipped += mode_result.skipped
            else:
                logger.warning(f"Unsupported mode: {mode}")

        return result

    async def _download_user_post(self, sec_uid: str, user_info: Dict[str, Any]) -> DownloadResult:
        result = DownloadResult()
        aweme_list = []
        max_cursor = 0
        has_more = True

        increase_enabled = self.config.get('increase', {}).get('post', False)
        latest_time = None

        if increase_enabled and self.database:
            latest_time = await self.database.get_latest_aweme_time(user_info.get('uid'))

        while has_more:
            await self.rate_limiter.acquire()

            data = await self.api_client.get_user_post(sec_uid, max_cursor)
            if not data:
                break

            aweme_items = data.get('aweme_list', [])
            if not aweme_items:
                break

            if increase_enabled and latest_time:
                new_items = [a for a in aweme_items if a.get('create_time', 0) > latest_time]
                aweme_list.extend(new_items)
                if len(new_items) < len(aweme_items):
                    break
            else:
                aweme_list.extend(aweme_items)

            has_more = data.get('has_more', False)
            max_cursor = data.get('max_cursor', 0)

            number_limit = self.config.get('number', {}).get('post', 0)
            if number_limit > 0 and len(aweme_list) >= number_limit:
                aweme_list = aweme_list[:number_limit]
                break

        aweme_list = self._filter_by_time(aweme_list)
        aweme_list = self._limit_count(aweme_list, 'post')

        result.total = len(aweme_list)

        author_name = user_info.get('nickname', 'unknown')

        async def _process_aweme(item: Dict[str, Any]):
            aweme_id = item.get('aweme_id')
            if not await self._should_download(aweme_id):
                return {'status': 'skipped', 'aweme_id': aweme_id}

            success = await self._download_aweme_assets(item, author_name, mode='post')
            return {
                'status': 'success' if success else 'failed',
                'aweme_id': aweme_id,
            }

        download_results = await self.queue_manager.download_batch(_process_aweme, aweme_list)

        for entry in download_results:
            status = entry.get('status') if isinstance(entry, dict) else None
            if status == 'success':
                result.success += 1
            elif status == 'failed':
                result.failed += 1
            elif status == 'skipped':
                result.skipped += 1
            else:
                result.failed += 1

        return result

    async def _download_user_like(self, sec_uid: str, user_info: Dict[str, Any]) -> DownloadResult:
        """下载用户喜欢的作品"""
        result = DownloadResult()
        aweme_list = []
        max_cursor = 0
        has_more = True

        increase_enabled = self.config.get('increase', {}).get('like', False)
        latest_time = None

        if increase_enabled and self.database:
            latest_time = await self.database.get_latest_aweme_time(user_info.get('uid'))

        # 获取喜欢的作品列表
        while has_more:
            await self.rate_limiter.acquire()

            data = await self.api_client.get_user_like(sec_uid, max_cursor)
            if not data:
                break

            aweme_items = data.get('aweme_list', [])
            if not aweme_items:
                break

            if increase_enabled and latest_time:
                new_items = [a for a in aweme_items if a.get('create_time', 0) > latest_time]
                aweme_list.extend(new_items)
                if len(new_items) < len(aweme_items):
                    break
            else:
                aweme_list.extend(aweme_items)

            has_more = data.get('has_more', False)
            max_cursor = data.get('max_cursor', 0)

            number_limit = self.config.get('number', {}).get('like', 0)
            if number_limit > 0 and len(aweme_list) >= number_limit:
                aweme_list = aweme_list[:number_limit]
                break

        aweme_list = self._filter_by_time(aweme_list)
        aweme_list = self._limit_count(aweme_list, 'like')

        result.total = len(aweme_list)
        author_name = user_info.get('nickname', 'unknown')

        async def _process_aweme(item: Dict[str, Any]):
            aweme_id = item.get('aweme_id')
            if not await self._should_download(aweme_id):
                return {'status': 'skipped', 'aweme_id': aweme_id}

            success = await self._download_aweme_assets(item, author_name, mode='like')
            return {
                'status': 'success' if success else 'failed',
                'aweme_id': aweme_id,
            }

        download_results = await self.queue_manager.download_batch(_process_aweme, aweme_list)

        for entry in download_results:
            status = entry.get('status') if isinstance(entry, dict) else None
            if status == 'success':
                result.success += 1
            elif status == 'failed':
                result.failed += 1
            elif status == 'skipped':
                result.skipped += 1
            else:
                result.failed += 1

        return result

    async def _download_user_mix(self, sec_uid: str, user_info: Dict[str, Any]) -> DownloadResult:
        """下载用户的合集"""
        result = DownloadResult()
        
        # 获取用户的合集列表
        await self.rate_limiter.acquire()
        mix_data = await self.api_client.get_user_mix_list(sec_uid)
        
        if not mix_data:
            logger.warning(f"No mix data found for user: {sec_uid}")
            return result
        
        mix_list = mix_data.get('mix_infos', [])
        if not mix_list:
            logger.info(f"User has no mixes: {sec_uid}")
            return result
        
        # 限制合集数量
        allmix_limit = self.config.get('number', {}).get('allmix', 0)
        if allmix_limit > 0:
            mix_list = mix_list[:allmix_limit]
        
        logger.info(f"Found {len(mix_list)} mix(es) for user: {sec_uid}")
        
        author_name = user_info.get('nickname', 'unknown')
        
        # 遍历每个合集
        for mix_info in mix_list:
            mix_id = mix_info.get('mix_id')
            mix_name = mix_info.get('mix_name', 'unknown_mix')
            
            logger.info(f"Processing mix: {mix_name} ({mix_id})")
            
            # 获取合集中的作品
            aweme_list = []
            cursor = 0
            has_more = True
            
            while has_more:
                await self.rate_limiter.acquire()
                
                mix_detail = await self.api_client.get_mix_detail(mix_id, cursor)
                if not mix_detail:
                    break
                
                aweme_items = mix_detail.get('aweme_list', [])
                if not aweme_items:
                    break
                
                aweme_list.extend(aweme_items)
                
                has_more = mix_detail.get('has_more', False)
                cursor = mix_detail.get('cursor', 0)
                
                # 限制每个合集的作品数量
                mix_limit = self.config.get('number', {}).get('mix', 0)
                if mix_limit > 0 and len(aweme_list) >= mix_limit:
                    aweme_list = aweme_list[:mix_limit]
                    break
            
            result.total += len(aweme_list)
            
            # 下载合集中的作品
            for item in aweme_list:
                aweme_id = item.get('aweme_id')
                if not await self._should_download(aweme_id):
                    result.skipped += 1
                    continue
                
                success = await self._download_aweme_assets(item, author_name, mode=f'mix/{mix_name}')
                if success:
                    result.success += 1
                else:
                    result.failed += 1
        
        return result
