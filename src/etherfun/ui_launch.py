"""Launch UI controller - Token launch wizard via buttons.

Flow:
1. Intro - explain what launching does
2. Symbol - enter token symbol (text input)
3. Name - enter token name (text input)
4. Supply - select from presets or custom
5. Liquidity - select ETH amount from presets or custom
6. Confirm - review all details
7. Sign - link to MetaMask widget
8. Success - show token links

All navigation via inline buttons. No separate /launch command.
"""

from __future__ import annotations

import re
from typing import Dict

from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from monitoring.observe import observe

from bot.ui_controllers.base import BaseController, BACK_STACK
from storage import ui_sessions
from localization import get_text
from localization.translator import get_user_language
import logging

logger = logging.getLogger(__name__)


class LaunchController(BaseController):
    """Handle token launch wizard via dashboard buttons."""

    def _get_launcher(self):
        """Get or create TokenLauncher instance."""
        if not hasattr(self, '_token_launcher'):
            from agents.siah.etherfun import TokenLauncher, WEB3_AVAILABLE
            if not WEB3_AVAILABLE or TokenLauncher is None:
                self._token_launcher = None
            else:
                self._token_launcher = TokenLauncher()
        return self._token_launcher

    def _get_launch_data(self, user_id: int) -> dict:
        """Get launch data from session."""
        session = ui_sessions.get_session(user_id)
        return session.get("launch_data", {})

    def _set_launch_data(self, user_id: int, data: dict) -> None:
        """Store launch data in session."""
        ui_sessions.update_session(user_id, launch_data=data)

    def _clear_launch_data(self, user_id: int) -> None:
        """Clear launch data from session."""
        ui_sessions.update_session(user_id, launch_data=None, awaiting_input=None)

    @observe("launch.handle_intro", skip_params={"context"})
    async def handle_intro(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: Dict[str, str],
    ) -> None:
        """Step 0: Introduction screen."""
        await self.answer_callback(update)
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)

        # Check web3 availability
        launcher = self._get_launcher()
        if launcher is None:
            await self.edit_panel(
                update,
                get_text("launch.title", lang),
                get_text("launch.unavailable_body", lang),
                [],
                back_callback="dashboard|main|v1",
            )
            return

        # Clear any previous launch data
        self._clear_launch_data(user_id)

        body = get_text("launch.intro_body", lang)

        buttons = [
            [InlineKeyboardButton(get_text("launch.btn_start", lang), callback_data="launch|symbol|v1")],
        ]

        await self.edit_panel(
            update,
            get_text("launch.title", lang),
            body,
            buttons,
            back_callback="dashboard|main|v1",
        )

    @observe("launch.handle_symbol", skip_params={"context"})
    async def handle_symbol(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: Dict[str, str],
    ) -> None:
        """Step 1: Enter token symbol."""
        await self.answer_callback(update)
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)

        # Set awaiting input for symbol
        ui_sessions.update_session(
            user_id,
            awaiting_input="launch_symbol",
            return_to="launch|name|v1",
        )

        body = get_text("launch.symbol_body", lang)

        await self.edit_panel(
            update,
            get_text("launch.symbol_title", lang),
            body,
            [],
            back_callback="launch|intro|v1",
        )

    @observe("launch.handle_name", skip_params={"context"})
    async def handle_name(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: Dict[str, str],
    ) -> None:
        """Step 2: Enter token name."""
        await self.answer_callback(update)
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)

        data = self._get_launch_data(user_id)
        symbol = data.get("symbol", "???")

        # Set awaiting input for name
        ui_sessions.update_session(
            user_id,
            awaiting_input="launch_name",
            return_to="launch|supply|v1",
        )

        body = get_text("launch.name_body", lang, symbol=symbol)

        await self.edit_panel(
            update,
            get_text("launch.name_title", lang),
            body,
            [],
            back_callback="launch|symbol|v1",
        )

    @observe("launch.handle_supply", skip_params={"context"})
    async def handle_supply(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: Dict[str, str],
    ) -> None:
        """Step 3: Select token supply."""
        await self.answer_callback(update)
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)

        data = self._get_launch_data(user_id)
        symbol = data.get("symbol", "???")
        name = data.get("name", "???")

        # Clear any awaiting input
        ui_sessions.update_session(user_id, awaiting_input=None)

        body = get_text("launch.supply_body", lang, symbol=symbol, name=name)

        buttons = [
            [
                InlineKeyboardButton(get_text("launch.btn_1b", lang), callback_data="launch|set_supply|v1|amt=1000000000"),
                InlineKeyboardButton(get_text("launch.btn_100m", lang), callback_data="launch|set_supply|v1|amt=100000000"),
            ],
            [
                InlineKeyboardButton(get_text("launch.btn_10m", lang), callback_data="launch|set_supply|v1|amt=10000000"),
                InlineKeyboardButton(get_text("launch.btn_1m", lang), callback_data="launch|set_supply|v1|amt=1000000"),
            ],
            [InlineKeyboardButton(get_text("launch.btn_custom", lang), callback_data="launch|custom_supply|v1")],
        ]

        await self.edit_panel(
            update,
            get_text("launch.supply_title", lang),
            body,
            buttons,
            back_callback="launch|name|v1",
        )

    @observe("launch.handle_set_supply", skip_params={"context"})
    async def handle_set_supply(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: Dict[str, str],
    ) -> None:
        """Handle supply button selection."""
        await self.answer_callback(update)
        user_id = update.effective_user.id if update.effective_user else 0

        supply = int(params.get("amt", 1000000000))

        data = self._get_launch_data(user_id)
        data["supply"] = supply
        self._set_launch_data(user_id, data)

        # Go to liquidity step
        await self.handle_liquidity(update, context, params)

    @observe("launch.handle_custom_supply", skip_params={"context"})
    async def handle_custom_supply(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: Dict[str, str],
    ) -> None:
        """Handle custom supply input."""
        await self.answer_callback(update)
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)

        data = self._get_launch_data(user_id)
        symbol = data.get("symbol", "???")
        name = data.get("name", "???")

        ui_sessions.update_session(
            user_id,
            awaiting_input="launch_supply",
            return_to="launch|liquidity|v1",
        )

        body = get_text("launch.custom_supply_body", lang, symbol=symbol, name=name)

        await self.edit_panel(
            update,
            get_text("launch.custom_supply_title", lang),
            body,
            [],
            back_callback="launch|supply|v1",
        )

    @observe("launch.handle_liquidity", skip_params={"context"})
    async def handle_liquidity(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: Dict[str, str],
    ) -> None:
        """Step 4: Select ETH liquidity amount."""
        await self.answer_callback(update)
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)

        data = self._get_launch_data(user_id)
        symbol = data.get("symbol", "???")
        name = data.get("name", "???")
        supply = data.get("supply", 0)

        # Format supply
        if supply >= 1_000_000_000:
            supply_str = f"{supply / 1_000_000_000:.1f}B".rstrip('0').rstrip('.')
        elif supply >= 1_000_000:
            supply_str = f"{supply / 1_000_000:.1f}M".rstrip('0').rstrip('.')
        else:
            supply_str = f"{supply:,}"

        body = get_text("launch.liquidity_body", lang, symbol=symbol, name=name, supply=supply_str)

        buttons = [
            [
                InlineKeyboardButton(get_text("launch.btn_01_eth", lang), callback_data="launch|set_eth|v1|amt=0.1"),
                InlineKeyboardButton(get_text("launch.btn_025_eth", lang), callback_data="launch|set_eth|v1|amt=0.25"),
            ],
            [
                InlineKeyboardButton(get_text("launch.btn_05_eth", lang), callback_data="launch|set_eth|v1|amt=0.5"),
                InlineKeyboardButton(get_text("launch.btn_1_eth", lang), callback_data="launch|set_eth|v1|amt=1"),
            ],
            [InlineKeyboardButton(get_text("launch.btn_custom", lang), callback_data="launch|custom_eth|v1")],
        ]

        await self.edit_panel(
            update,
            get_text("launch.liquidity_title", lang),
            body,
            buttons,
            back_callback="launch|supply|v1",
        )

    @observe("launch.handle_set_eth", skip_params={"context"})
    async def handle_set_eth(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: Dict[str, str],
    ) -> None:
        """Handle ETH amount button selection."""
        await self.answer_callback(update)
        user_id = update.effective_user.id if update.effective_user else 0

        eth_amount = float(params.get("amt", 0.1))

        data = self._get_launch_data(user_id)
        data["eth_liquidity"] = eth_amount
        self._set_launch_data(user_id, data)

        # Go to confirm step
        await self.handle_confirm(update, context, params)

    @observe("launch.handle_custom_eth", skip_params={"context"})
    async def handle_custom_eth(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: Dict[str, str],
    ) -> None:
        """Handle custom ETH input."""
        await self.answer_callback(update)
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)

        ui_sessions.update_session(
            user_id,
            awaiting_input="launch_eth",
            return_to="launch|confirm|v1",
        )

        body = get_text("launch.custom_eth_body", lang)

        await self.edit_panel(
            update,
            get_text("launch.custom_eth_title", lang),
            body,
            [],
            back_callback="launch|liquidity|v1",
        )

    @observe("launch.handle_confirm", skip_params={"context"})
    async def handle_confirm(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: Dict[str, str],
    ) -> None:
        """Step 5: Review and confirm launch."""
        await self.answer_callback(update)
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)

        data = self._get_launch_data(user_id)
        symbol = data.get("symbol", "???")
        name = data.get("name", "???")
        supply = data.get("supply", 0)
        eth = data.get("eth_liquidity", 0)

        # Format supply
        if supply >= 1_000_000_000:
            supply_str = f"{supply / 1_000_000_000:.1f}B".rstrip('0').rstrip('.')
        elif supply >= 1_000_000:
            supply_str = f"{supply / 1_000_000:.1f}M".rstrip('0').rstrip('.')
        else:
            supply_str = f"{supply:,}"

        # Get gas estimate
        launcher = self._get_launcher()
        try:
            gas_estimate = launcher.get_gas_estimate()
            gas_usd = gas_estimate.total_cost_eth * 2500
            gas_str = f"~${gas_usd:.2f}"
        except Exception:
            gas_str = "~$5-10"

        body = get_text("launch.confirm_body", lang, symbol=symbol, name=name, supply=supply_str, eth=eth, gas=gas_str)

        buttons = [
            [InlineKeyboardButton(get_text("launch.btn_launch_now", lang), callback_data="launch|sign|v1")],
        ]

        await self.edit_panel(
            update,
            get_text("launch.confirm_title", lang),
            body,
            buttons,
            back_callback="launch|liquidity|v1",
        )

    @observe("launch.handle_sign", skip_params={"context"})
    async def handle_sign(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: Dict[str, str],
    ) -> None:
        """Step 6: Generate signing link."""
        await self.answer_callback(update)
        user_id = update.effective_user.id if update.effective_user else 0
        chat_id = update.effective_chat.id if update.effective_chat else 0
        lang = get_user_language(user_id)

        data = self._get_launch_data(user_id)
        symbol = data.get("symbol", "TOKEN")
        name = data.get("name", "Token")
        supply = data.get("supply", 1000000000)
        eth = data.get("eth_liquidity", 0.1)

        # Create launch session
        launcher = self._get_launcher()
        session, errors = launcher.create_session(
            name=name,
            symbol=symbol,
            supply=supply,
            eth_liquidity=eth,
            user_id=user_id,
            chat_id=chat_id,
        )

        if errors:
            error_list = "\n".join(f"• {e}" for e in errors)
            await self.edit_panel(
                update,
                get_text("launch.validation_error_title", lang),
                get_text("launch.validation_error_body", lang, errors=error_list),
                [],
                back_callback="launch|confirm|v1",
            )
            return

        # Store session ID
        data["session_id"] = session.session_id
        self._set_launch_data(user_id, data)

        # Generate signing URL
        signing_url = session.signing_url

        body = get_text("launch.sign_body", lang, signing_url=signing_url)

        buttons = [
            [InlineKeyboardButton(get_text("launch.btn_open_signing", lang), url=signing_url)],
        ]

        await self.edit_panel(
            update,
            get_text("launch.sign_title", lang),
            body,
            buttons,
            back_callback="launch|confirm|v1",
        )

    @observe("launch.handle_success", skip_params={"context"})
    async def handle_success(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: Dict[str, str],
    ) -> None:
        """Step 7: Show success with links."""
        await self.answer_callback(update)
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)

        token_address = params.get("token", "0x...")
        pair_address = params.get("pair")

        data = self._get_launch_data(user_id)
        symbol = data.get("symbol", "TOKEN")

        # Clear launch data
        self._clear_launch_data(user_id)

        token_short = f"{token_address[:10]}...{token_address[-6:]}"
        pair_short = f"{pair_address[:10]}...{pair_address[-6:]}" if pair_address else ""

        body = get_text("launch.success_body", lang, token=token_short, pair=pair_short, has_pair=bool(pair_address))

        buttons = [
            [InlineKeyboardButton(get_text("launch.btn_trade", lang), url=f"https://etherfun.app/token/{token_address}")],
        ]

        if pair_address:
            buttons.append([InlineKeyboardButton(get_text("launch.btn_chart", lang), url=f"https://dexscreener.com/ethereum/{pair_address}")])

        buttons.append([InlineKeyboardButton(get_text("launch.btn_etherscan", lang), url=f"https://etherscan.io/token/{token_address}")])

        await self.edit_panel(
            update,
            get_text("launch.success_title", lang, symbol=symbol),
            body,
            buttons,
            back_callback="dashboard|main|v1",
        )

    @observe("launch.handle_text_input", skip_params={"context"})
    async def handle_text_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        awaiting: str,
        text: str,
    ) -> bool:
        """Handle text input from message handler.

        Returns True if handled, False otherwise.
        """
        user_id = update.effective_user.id if update.effective_user else 0
        logger.info(f"[LAUNCH] Processing text input: awaiting={awaiting}, user={user_id}")

        if awaiting == "launch_symbol":
            return await self._handle_symbol_input(update, context, text)
        elif awaiting == "launch_name":
            return await self._handle_name_input(update, context, text)
        elif awaiting == "launch_supply":
            return await self._handle_supply_input(update, context, text)
        elif awaiting == "launch_eth":
            return await self._handle_eth_input(update, context, text)

        return False

    @observe("launch.handle_symbol_input", skip_params={"context"})
    async def _handle_symbol_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
    ) -> bool:
        """Process symbol text input."""
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)
        symbol = text.strip().upper()
        logger.info(f"[LAUNCH] Symbol input: {symbol}, user={user_id}")

        # Validate
        if not re.match(r'^[A-Za-z0-9]+$', symbol):
            await update.message.reply_text(get_text("launch.error_symbol_alphanumeric", lang))
            return True

        if len(symbol) < 2 or len(symbol) > 8:
            await update.message.reply_text(get_text("launch.error_symbol_length", lang))
            return True

        # Store and advance to name step
        data = self._get_launch_data(user_id)
        data["symbol"] = symbol
        self._set_launch_data(user_id, data)

        # Set awaiting for next step (name input)
        ui_sessions.update_session(
            user_id,
            awaiting_input="launch_name",
            return_to="launch|supply|v1",
        )

        # Show confirmation and prompt for name
        body = get_text("launch.name_body", lang, symbol=symbol)

        await update.message.reply_text(body, parse_mode="Markdown")
        return True

    @observe("launch.handle_name_input", skip_params={"context"})
    async def _handle_name_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
    ) -> bool:
        """Process name text input."""
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)
        name = text.strip().strip('"\'')
        logger.info(f"[LAUNCH] Name input: {name}, user={user_id}")

        if len(name) < 2 or len(name) > 64:
            await update.message.reply_text(get_text("launch.error_name_length", lang))
            return True

        data = self._get_launch_data(user_id)
        data["name"] = name
        self._set_launch_data(user_id, data)
        symbol = data.get("symbol", "???")

        # Clear awaiting - next step uses buttons
        ui_sessions.update_session(user_id, awaiting_input=None)

        # Format supply for display
        body = get_text("launch.supply_body", lang, symbol=symbol, name=name)

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        buttons = [
            [
                InlineKeyboardButton(get_text("launch.btn_1b", lang), callback_data="launch|set_supply|v1|amt=1000000000"),
                InlineKeyboardButton(get_text("launch.btn_100m", lang), callback_data="launch|set_supply|v1|amt=100000000"),
            ],
            [
                InlineKeyboardButton(get_text("launch.btn_10m", lang), callback_data="launch|set_supply|v1|amt=10000000"),
                InlineKeyboardButton(get_text("launch.btn_1m", lang), callback_data="launch|set_supply|v1|amt=1000000"),
            ],
            [InlineKeyboardButton(get_text("launch.btn_custom", lang), callback_data="launch|custom_supply|v1")],
            [InlineKeyboardButton(get_text("buttons.back", lang), callback_data="launch|symbol|v1")],
        ]

        await update.message.reply_text(
            f"{get_text('launch.supply_title', lang)}\n\n{body}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return True

    @observe("launch.handle_supply_input", skip_params={"context"})
    async def _handle_supply_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
    ) -> bool:
        """Process supply text input."""
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)
        logger.info(f"[LAUNCH] Supply input: {text}, user={user_id}")

        try:
            text = text.strip().upper().replace(',', '').replace(' ', '')

            if text.endswith('B'):
                supply = int(float(text[:-1]) * 1_000_000_000)
            elif text.endswith('M'):
                supply = int(float(text[:-1]) * 1_000_000)
            elif text.endswith('K'):
                supply = int(float(text[:-1]) * 1_000)
            else:
                supply = int(float(text))

            if supply < 1_000_000:
                await update.message.reply_text(get_text("launch.error_supply_low", lang))
                return True
            if supply > 1_000_000_000_000_000:
                await update.message.reply_text(get_text("launch.error_supply_high", lang))
                return True

        except ValueError:
            await update.message.reply_text(get_text("launch.error_supply_invalid", lang))
            return True

        data = self._get_launch_data(user_id)
        data["supply"] = supply
        self._set_launch_data(user_id, data)
        symbol = data.get("symbol", "???")
        name = data.get("name", "???")

        # Clear awaiting - next step uses buttons
        ui_sessions.update_session(user_id, awaiting_input=None)

        # Format supply for display
        if supply >= 1_000_000_000:
            supply_str = f"{supply / 1_000_000_000:.1f}B".rstrip('0').rstrip('.')
        elif supply >= 1_000_000:
            supply_str = f"{supply / 1_000_000:.1f}M".rstrip('0').rstrip('.')
        else:
            supply_str = f"{supply:,}"

        body = get_text("launch.liquidity_body", lang, symbol=symbol, name=name, supply=supply_str)

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        buttons = [
            [
                InlineKeyboardButton(get_text("launch.btn_01_eth", lang), callback_data="launch|set_eth|v1|amt=0.1"),
                InlineKeyboardButton(get_text("launch.btn_025_eth", lang), callback_data="launch|set_eth|v1|amt=0.25"),
            ],
            [
                InlineKeyboardButton(get_text("launch.btn_05_eth", lang), callback_data="launch|set_eth|v1|amt=0.5"),
                InlineKeyboardButton(get_text("launch.btn_1_eth", lang), callback_data="launch|set_eth|v1|amt=1"),
            ],
            [InlineKeyboardButton(get_text("launch.btn_custom", lang), callback_data="launch|custom_eth|v1")],
            [InlineKeyboardButton(get_text("buttons.back", lang), callback_data="launch|supply|v1")],
        ]

        await update.message.reply_text(
            f"{get_text('launch.liquidity_title', lang)}\n\n{body}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return True

    @observe("launch.handle_eth_input", skip_params={"context"})
    async def _handle_eth_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
    ) -> bool:
        """Process ETH amount text input."""
        user_id = update.effective_user.id if update.effective_user else 0
        lang = get_user_language(user_id)
        logger.info(f"[LAUNCH] ETH input: {text}, user={user_id}")

        try:
            eth = float(text.strip().replace(',', ''))

            if eth < 0.01:
                await update.message.reply_text(get_text("launch.error_eth_low", lang))
                return True
            if eth > 100:
                await update.message.reply_text(get_text("launch.error_eth_high", lang))
                return True

        except ValueError:
            await update.message.reply_text(get_text("launch.error_eth_invalid", lang))
            return True

        data = self._get_launch_data(user_id)
        data["eth_liquidity"] = eth
        self._set_launch_data(user_id, data)
        symbol = data.get("symbol", "???")
        name = data.get("name", "???")
        supply = data.get("supply", 0)

        # Clear awaiting
        ui_sessions.update_session(user_id, awaiting_input=None)

        # Format supply for display
        if supply >= 1_000_000_000:
            supply_str = f"{supply / 1_000_000_000:.1f}B".rstrip('0').rstrip('.')
        elif supply >= 1_000_000:
            supply_str = f"{supply / 1_000_000:.1f}M".rstrip('0').rstrip('.')
        else:
            supply_str = f"{supply:,}"

        # Get gas estimate
        launcher = self._get_launcher()
        try:
            gas_estimate = launcher.get_gas_estimate()
            gas_usd = gas_estimate.total_cost_eth * 2500
            gas_str = f"~${gas_usd:.2f}"
        except Exception:
            gas_str = "~$5-10"

        body = get_text("launch.confirm_body", lang, symbol=symbol, name=name, supply=supply_str, eth=eth, gas=gas_str)

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        buttons = [
            [InlineKeyboardButton(get_text("launch.btn_launch_now", lang), callback_data="launch|sign|v1")],
            [InlineKeyboardButton(get_text("buttons.back", lang), callback_data="launch|liquidity|v1")],
        ]

        await update.message.reply_text(
            f"{get_text('launch.confirm_title', lang)}\n\n{body}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return True
