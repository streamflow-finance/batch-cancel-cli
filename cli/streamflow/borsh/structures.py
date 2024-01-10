from podite import F32, U8, U32, U64, FixedLenArray, pod


@pod
class Contract:
    magic: U64
    version: U8
    created_at: U64
    withdrawn_amount: U64
    canceled_at: U64
    end_time: U64
    last_withdrawn: U64
    sender: FixedLenArray[U8, 32]
    sender_tokens: FixedLenArray[U8, 32]
    recipient: FixedLenArray[U8, 32]
    recipient_tokens: FixedLenArray[U8, 32]
    mint: FixedLenArray[U8, 32]
    escrow_tokens: FixedLenArray[U8, 32]
    streamflow_treasury: FixedLenArray[U8, 32]
    streamflow_treasury_tokens: FixedLenArray[U8, 32]
    streamflow_fee: U64
    streamflow_fee_withdrawn: U64
    streamflow_fee_percentage: F32
    partner: FixedLenArray[U8, 32]
    partner_tokens: FixedLenArray[U8, 32]
    partner_fee: U64
    partner_fee_withdrawn: U64
    partner_fee_percentage: F32
    start_time: U64
    net_amount_deposited: U64
    period: U64
    amount_per_period: U64
    cliff: U64
    cliff_amount: U64
    cancelable_by_sender: U8
    cancelable_by_recipient: U8
    automatic_withdrawal: U8
    transferable_by_sender: U8
    transferable_by_recipient: U8
    can_topup: U8
    name: FixedLenArray[U8, 64]
    withdrawal_frequency: U64
    ghost: U32
    pausable: U8
    can_update_rate: U8
    padding: FixedLenArray[U8, 130]
    closed: U8
    current_pause_start: U64
    pause_cumulative: U64
    last_rate_change_time: U64
    funds_unlocked_at_last_rate_change: U64
