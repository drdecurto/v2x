"""Explicit trace alignment; never infer missing transmissions from RX alone."""
import pandas as pd

def align_packets(tx,rx):
    tx=tx.copy();rx=rx.copy()
    if 'extra' in rx:
        rx=rx.loc[rx['extra']==0].copy()
    keys=['tx_equipment_id','seq','tx_us']
    tx=tx.rename(columns={'seq_num':'seq','timestamp':'tx_us'})
    rx=rx.rename(columns={'tx_seq_num':'seq','tx_timestamp (us)':'tx_us','rx_timestamp (us)':'rx_us'})
    for frame in (tx,rx):
        if frame[keys].isna().any().any():raise ValueError('Missing packet identity')
        frame[keys]=frame[keys].astype('int64')
    if tx.duplicated(keys).any() or rx.duplicated(keys).any():raise ValueError('Duplicate packet identity; inspect before proceeding')
    paired=tx.merge(rx[keys+['rx_us','latency (ms)']],on=keys,how='left',validate='one_to_one')
    matched=paired['rx_us'].notna()
    if not matched.any():raise ValueError('No matched TX/RX packets')
    lo,hi=paired.loc[matched,'tx_us'].min(),paired.loc[matched,'tx_us'].max()
    # Traces do not document receiver logging start/end. Restrict to matched
    # observation support; boundary loss is unidentifiable and excluded explicitly.
    window=paired.loc[paired.tx_us.between(lo,hi)].copy().sort_values('tx_us')
    window['received']=window.rx_us.notna()
    window['delay_s']=(window.rx_us-window.tx_us)/1e6
    if (window.loc[window.received,'delay_s']<0).any():raise ValueError('Negative delay: synchronization requires investigation')
    residual=(window.loc[window.received,'delay_s']*1000-window.loc[window.received,'latency (ms)']).abs()
    if residual.max()>0.01:raise ValueError('Timestamp units disagree with recorded latency')
    window['tx_offset_s']=(window.tx_us-window.tx_us.min())/1e6
    return window,{'tx_total':len(tx),'rx_original':len(rx),'rx_unmatched':len(rx)-int(matched.sum()),'boundary_tx_excluded':int(len(tx)-len(window)),'observed_tx':len(window),'received':int(window.received.sum()),'pdr':float(window.received.mean()),'negative_delays':0,'clock_note':'Delay agrees with source fields; independent clock-synchronization uncertainty remains to be verified from paper.'}
