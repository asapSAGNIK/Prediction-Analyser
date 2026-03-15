import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

interface ControlsProps {
    startTime: Date;
    endTime: Date;
    forecastHorizon: number;
    onStartTimeChange: (date: Date) => void;
    onEndTimeChange: (date: Date) => void;
    onHorizonChange: (hours: number) => void;
}

export function Controls({
    startTime,
    endTime,
    forecastHorizon,
    onStartTimeChange,
    onEndTimeChange,
    onHorizonChange,
}: ControlsProps) {
    // Constrain to January 2024 data
    const minDate = new Date('2024-01-01T00:00:00Z');
    const maxDate = new Date('2024-01-31T23:59:59Z');

    return (
        <div className="controls" id="controls-panel">
            <div className="control-group">
                <label className="control-group__label" htmlFor="start-time">
                    Start Time
                </label>
                <DatePicker
                    id="start-time"
                    selected={startTime}
                    onChange={(date) => date && onStartTimeChange(date)}
                    showTimeSelect
                    timeIntervals={30}
                    dateFormat="dd/MM/yyyy HH:mm"
                    timeFormat="HH:mm"
                    minDate={minDate}
                    maxDate={endTime}
                    placeholderText="Select start time"
                />
            </div>

            <div className="control-group">
                <label className="control-group__label" htmlFor="end-time">
                    End Time
                </label>
                <DatePicker
                    id="end-time"
                    selected={endTime}
                    onChange={(date) => date && onEndTimeChange(date)}
                    showTimeSelect
                    timeIntervals={30}
                    dateFormat="dd/MM/yyyy HH:mm"
                    timeFormat="HH:mm"
                    minDate={startTime}
                    maxDate={maxDate}
                    placeholderText="Select end time"
                />
            </div>

            <div className="control-group">
                <label className="control-group__label">
                    Forecast Horizon
                </label>
                <div className="horizon-display">
                    <span className="horizon-value">{forecastHorizon}</span>
                    <span className="horizon-unit">hours</span>
                </div>
                <input
                    id="horizon-slider"
                    type="range"
                    min={0}
                    max={48}
                    step={1}
                    value={forecastHorizon}
                    onChange={(e) => onHorizonChange(Number(e.target.value))}
                    aria-label="Forecast horizon in hours"
                />
            </div>
        </div>
    );
}
